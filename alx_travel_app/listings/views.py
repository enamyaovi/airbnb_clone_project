from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action, api_view
from listings.models import Booking, Listing, Review, Payment
from listings.tasks import send_booking_confirmation_email
from listings.serializers import (
    UserSerializer, BookingSerializer, ListingSerializer, 
    UserRegisterSerializer, 
    InitiatePaymentRequestSerializer, InitiatePaymentResponseSerializer,
    PaymentResponseSerializer, PaymentStatusSerializer
)

from listings.permissions import IsAdminOrAnonymous, IsAdminOrUserOwner, IsAdminOrBookingUser

from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
import requests, json, hmac, hashlib
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotAllowed

# from drf_yasg.utils import swagger_auto_schema
from drf_spectacular.utils import extend_schema, OpenApiResponse

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts.
    Only authenticated users can access this endpoint.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create' or self.request.method == 'OPTIONS':
            self.permission_classes = [IsAdminOrAnonymous]
        if self.action in ['update','partial_update', 'destroy']:
            self.permission_classes = [IsAdminOrUserOwner]
        return super().get_permissions()
    
    def get_serializer_class(self): # type: ignore
        if self.action == 'create' or self.request.method == 'OPTIONS':
            return UserRegisterSerializer
        return super().get_serializer_class()


class BookingViewSet(viewsets.ModelViewSet):
    """
    Handles confirmed bookings.
    Authenticated users can create; others can read.
    """
    queryset = Booking.objects.prefetch_related('booking_payment').all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]



    def perform_create(self, serializer):
        """
        Automatically set the booking's customer to the logged-in user.
        """
        booking = serializer.save(customer=self.request.user)
        
        send_booking_confirmation_email.delay( # type: ignore
            to_email=self.request.user.email, # type: ignore
            booking_id=booking.id,
            listing_title=booking.listing.title,
            booking_date=str(booking.date),
        )

    def get_queryset(self): # type: ignore
        if self.request.user.is_authenticated:
            return Booking.objects.filter(customer=self.request.user)
        return super().get_queryset()
    
    def get_permissions(self):
        if self.action in ['initiate_payment', 'verify_payment']:
            self.permission_classes = [IsAdminOrBookingUser]
        return super().get_permissions()
    
    def _initiate_payment_request(self,payload):
        payment_url = settings.PAYMENT_API_BASE_URL
        headers = {
            'Authorization':f'Bearer {settings.PAYMENT_API_KEY}',
            'Content-Type':'application/json'
        }

        response = requests.post(url=payment_url, json=payload, headers=headers)
        return response.json()
    
    def _request_payment_api(self, payment, booking, re_initiate=False):
        merchant_ref = Payment.generate_merchant_reference()
        payload = {
            "amount": str(payment.amount),
            "currency": payment.currency,
            "email": booking.customer.email,
            "tx_ref": merchant_ref,
            "callback_url": settings.WEBHOOK_URL,
        }
        headers = {
            'Authorization': f'Bearer {settings.PAYMENT_API_KEY}',
            'Content-Type': 'application/json'
        }

        resp = requests.post(settings.PAYMENT_API_BASE_URL, json=payload, headers=headers)
        data = resp.json()

        if data.get('status') != 'success':
            return Response({"status": data.get('status'), "msg": data.get('message')}, status=status.HTTP_400_BAD_REQUEST)

        payment.checkout_url = data['data']['checkout_url']
        payment.payment_status = Payment.PaymentStatus.PROCESSING
        payment.raw_request = payload
        payment.raw_response = data
        payment.save()

        return Response({"msg": "Payment re-initiated. Click Redirect Link to Pay", "redirect_url": payment.checkout_url}, status=status.HTTP_200_OK)
    

    @extend_schema(
        request=None,
        responses={200: PaymentStatusSerializer},
        methods=['GET'],
        description="Retrieve booking and payment status for this booking."
    )
    @extend_schema(
        request=InitiatePaymentRequestSerializer,
        responses={
            200: PaymentResponseSerializer,
            202: OpenApiResponse(response=PaymentResponseSerializer, description="Booking confirmed"),
            400: OpenApiResponse(response=PaymentResponseSerializer, description="Booking not pending or API error"),
            424: OpenApiResponse(response=PaymentResponseSerializer, description="Payment failed or cancelled"),
        },
        methods=['POST'],
        description="Initiate or re-initiate payment for this booking."
    )
    @action(detail=True, methods=['post', 'get'])
    def initiate_payment(self, request, pk=None):
        
        booking = self.get_object()
        payment = Payment.objects.filter(booking_reference=booking).first()

        if request.method == 'GET':
            return Response(
                {
                "Booking-Details":{
                "booking_status": booking.status,
                "payment_status": payment.payment_status if payment else None,
                "checkout_url":payment.checkout_url if payment else None}
                }, status=status.HTTP_200_OK)
        
        if request.method == 'POST':
            if booking.status != Booking.BookingStatus.PENDING:
                return Response(
                    {"msg":"Booking is not pending"},
                    status=status.HTTP_400_BAD_REQUEST)
            
            if payment:
                if payment.payment_status == Payment.PaymentStatus.SUCCESS:
                    booking.status = Booking.BookingStatus.CONFIRMED
                    booking.save()
                    return Response(
                        {"msg":"Booking Confirmed"},
                        status=status.HTTP_202_ACCEPTED)
                
                elif payment.payment_status in [Payment.PaymentStatus.PENDING, Payment.PaymentStatus.PROCESSING]:
                    if payment.checkout_url:
                        return Response({
                            "msg":"Click the checkout link to pay",
                            "checkout": payment.checkout_url},
                            status=status.HTTP_200_OK)
                    else:
                        return self._request_payment_api(payment, booking,re_initiate=True)

                if payment.payment_status in ['CANCELLED', 'FAILED']:
                    return Response({
                        "msg": "Payment failed or cancelled"},
                        status=status.HTTP_424_FAILED_DEPENDENCY)
            else:
            # No payment exists → create a new one
                merchant_ref = Payment.generate_merchant_reference()
                amount = booking.total_price

                payment_payload = {
                    "amount": amount,
                    "currency": "ETB",
                    "email": request.user.email,
                    "tx_ref": merchant_ref,
                    "callback_url": settings.WEBHOOK_URL,
                }
                headers = {
                    'Authorization': f'Bearer {settings.PAYMENT_API_KEY}',
                    'Content-Type': 'application/json'
                }

                response = requests.post(settings.PAYMENT_API_BASE_URL, json=payment_payload, headers=headers)
                data = response.json()

                # Stop here if API key or business inactive
                if data.get('status') != 'success':
                    return Response(
                        {"status": data.get('status'), "msg": data.get('message')},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Create payment only if API call succeeded
                payment = Payment.objects.create(
                    booking_reference=booking,
                    amount=amount,
                    merchant_reference=merchant_ref,
                    payment_status=Payment.PaymentStatus.PROCESSING,
                    checkout_url=data['data']['checkout_url'],
                    raw_request=payment_payload,
                    raw_response=data
                )

                return Response(
                    {"msg": "Payment initiated", "redirect_url": payment.checkout_url},
                    status=status.HTTP_200_OK
                )
            
            

    @action(detail=True, methods=['post', 'get'])
    def verify_payment(self, request, pk=None):
        pass

    # @action(detail=True, methods=['post'])
    # def initiate_payment(self, request, pk=None):
# 
        # get the booking object
        # booking = self.get_object()
        # payment_url = settings.PAYMENT_API_BASE_URL
# 
        # check if the booking status is Pending
        # if booking.status == Booking.BookingStatus.PENDING:
            # payment, created = Payment.objects.get_or_create(
                # booking_reference=booking,
                # defaults={
                    # "amount":booking.total_price,
                    # "merchant_reference":Payment.generate_merchant_reference(),
                    # "payment_status":Payment.PaymentStatus.PENDING
                # })
            # 
            # if created:
            # New payment → build payload, call API, store checkout URL + status
                # payment_payload = {
                    # "amount":payment.amount,
                    # "currency":payment.currency,
                    # "email":self.request.user.email,
                    # "tx_ref":payment.merchant_reference,
                    # "callback_url":settings.WEBHOOK_URL,
                    # # "return_url":reverse_lazy('confirm') #will write this extra_action later
                # }
                # pay_headers = {
                    # 'Authorization': f'Bearer {settings.PAYMENT_API_KEY}',
                    # 'Content-Type': 'application/json'
                # }
# 
                # initiate handshake with Payment API
                # response = requests.post(
                    # url=payment_url, json=payment_payload, headers=pay_headers)
                # response_data = response.json()
                # 
                # if response_data.get('status') == 'success':
                    # # payment.checkout_url = response_data['data']['checkout_url']
                    # payment.payment_status = Payment.PaymentStatus.PROCESSING
                    # payment.raw_response = response_data
                    # payment.raw_request = payment_payload
                    # payment.save()
                    # return Response for success API communication
                    # return Response(
                            # data={
                                # "msg":"Payment Generated. Click on link pay",
                                # # "redirect_url":response_data['data']['checkout_url']},
                            # status=status.HTTP_200_OK)
                # return Response(
                    # data={
                        # "Status":response_data.get('status'),
                        # "msg":"try again"
                    # },
                    # status=status.HTTP_400_BAD_REQUEST)
# 
            # else:
                # if payment.payment_status == Payment.PaymentStatus.SUCCESS:
                    # booking.status = Booking.BookingStatus.CONFIRMED
                    # booking.save()
# 
                    # return Response(
                        # data={
                            # "msg":"Booking Confirmed"
                        # },
                        # status= status.HTTP_202_ACCEPTED)
                # 
                # elif payment.payment_status in ["PENDING", "PROCESSING"]:
                    # if payment.checkout_url:
                        # return Response(
                            # data={
                                # # "msg":"CheckOut Retrieved. Click on Link to pay",
                                # "checkout":payment.checkout_url
                            # },
                            # status=status.HTTP_200_OK)
                    # else:
                        # find a DRY way to re-initiate payment request
                        # new_payload= payment_payload.copy()
                        # # new_payload['tx_ref']=Payment.generate_merchant_reference()
# 
                        # n_response= requests.post(
                            # url=payment_url,
                            # json=new_payload,
                            # headers=pay_headers)
                        # 
                        # n_response_data = n_response.json()
# 
                        # if n_response_data.get('status') == 'success':
                            # # payment.checkout_url = n_response_data['data']['checkout_url']
                            # # payment.payment_status = Payment.PaymentStatus.PROCESSING
                            # payment.raw_response = n_response_data
                            # payment.raw_request = new_payload
                            # payment.save()
# 
                            # return Response(
                                # data={
                                    # # "msg":"Payment Generated. Click on link pay",
                                    # # "redirect_url":n_response_data['data']['checkout_url']},
                                # status=status.HTTP_200_OK)
                        # 
                        # return Response(
                            # data={
                                # "Status":n_response_data.get('status'),
                                # "msg":"try again"
                            # },
                            # status=status.HTTP_400_BAD_REQUEST
                        # )
# 
                # elif payment.payment_status in ["CANCELLED", "FAILED"]:
                    # return Response(
                        # data={
                            # # "msg":"Sorry Your Payment failed or was cancelled. Book again or apply for a refund"},
                        # status=status.HTTP_424_FAILED_DEPENDENCY
                    # )

        

class ListingViewSet(viewsets.ModelViewSet):
    """
    Manages listings. Anyone can read; only authenticated users can create/edit.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@api_view(['GET'])
def confirm(request):
    return Response({"msg":"dummy for now"})


@csrf_exempt
@api_view(['POST'])
def chapa_webhook(request):
    
    #take the raw body of the request from Chappa
    raw_body = request.body 
    raw_text = raw_body.decode('utf-8')

    #extract the signature header and confirm the keys match
    signature_header = request.headers.get('X-Chapa-Signature')
    print(request.headers)
    if not signature_header:
        return Response({"msg":"Missing Signature"}, status=status.HTTP_403_FORBIDDEN)
    
    expected = hmac.new(
        key=settings.WEBHOOK_SECRET.encode('utf-8'),
        msg=raw_body,
        digestmod=hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(signature_header, expected):
        return Response({"msg":"Invalid Signature"}, status=status.HTTP_403_FORBIDDEN)

    #parse the response to retrieve webhook reference and merchant reference
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        return Response({"ok": False, "error": "invalid json"}, status=status.HTTP_400_BAD_REQUEST)
    
    tx_ref = payload.get("tx_ref")
    if not tx_ref:
        return Response({"ok": False, "error": "missing tx_ref"}, status=status.HTTP_400_BAD_REQUEST)
    
    event_id = payload.get("reference")
    if not event_id:
        return Response({"ok":False, "error":"missing 'reference'"},
        status=status.HTTP_400_BAD_REQUEST)
    
    #confirm there exists a payment initiated with merchant id
    payment = Payment.objects.filter(merchant_reference=tx_ref).first()
    if not payment:
        return Response({"ok": True, "note": "no matching payment"}, status=status.HTTP_200_OK)
    
    if payment.payment_status == Payment.PaymentStatus.SUCCESS:
        return Response({"ok": True, "note": "already confirmed"}, status=status.HTTP_200_OK)
    
    #verify payment with chappa api
    verify_url = f"{settings.PAYMENT_VERIFY_URL}/{tx_ref}"
    headers = {"Authorization": f"Bearer {settings.PAYMENT_API_KEY}"}

    try:
        r = requests.get(verify_url, headers=headers, timeout=30)
        data = r.json()    

        #if successful update booking and payment instances
        if data.get('status') == 'success':
            payment = Payment.objects.select_related('booking_reference').get(
                merchant_reference=tx_ref
            )
            payment.payment_status = Payment.PaymentStatus.SUCCESS
            payment.webhook_event_id = event_id
            payment.save()

            booking = payment.booking_reference
            booking.status = Booking.BookingStatus.CONFIRMED
            booking.save()
        return Response({"msg": "Processed"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"ok": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
