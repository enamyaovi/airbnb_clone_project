BEGIN;
--
-- Create model CustomUser
--
CREATE TABLE "listings_customuser" ("password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "first_name" varchar(150) NOT NULL, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "user_id" char(32) NOT NULL PRIMARY KEY);
CREATE TABLE "listings_customuser_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "customuser_id" char(32) NOT NULL REFERENCES "listings_customuser" ("user_id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "listings_customuser_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "customuser_id" char(32) NOT NULL REFERENCES "listings_customuser" ("user_id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Listing
--
CREATE TABLE "listings_listing" ("listing_id" char(32) NOT NULL PRIMARY KEY, "name" varchar(100) NOT NULL, "description" text NOT NULL, "price_per_night" decimal NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "host_id" char(32) NOT NULL REFERENCES "listings_customuser" ("user_id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Booking
--
CREATE TABLE "listings_booking" ("booking_id" char(32) NOT NULL PRIMARY KEY, "start_date" date NOT NULL, "end_date" date NOT NULL, "total_price" integer NOT NULL, "status" varchar(3) NOT NULL, "created_at" datetime NOT NULL, "customer_id" char(32) NOT NULL REFERENCES "listings_customuser" ("user_id") DEFERRABLE INITIALLY DEFERRED, "listing_id" char(32) NOT NULL REFERENCES "listings_listing" ("listing_id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Review
--
CREATE TABLE "listings_review" ("review_id" char(32) NOT NULL PRIMARY KEY, "rating" smallint NOT NULL, "comment" text NULL, "created_at" datetime NOT NULL, "customer_id" char(32) NOT NULL REFERENCES "listings_customuser" ("user_id") DEFERRABLE INITIALLY DEFERRED, "listing_id" char(32) NOT NULL REFERENCES "listings_listing" ("listing_id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "listings_customuser_groups_customuser_id_group_id_73d30e92_uniq" ON "listings_customuser_groups" ("customuser_id", "group_id");
CREATE INDEX "listings_customuser_groups_customuser_id_38f2bee5" ON "listings_customuser_groups" ("customuser_id");
CREATE INDEX "listings_customuser_groups_group_id_6b748249" ON "listings_customuser_groups" ("group_id");
CREATE UNIQUE INDEX "listings_customuser_user_permissions_customuser_id_permission_id_e365c9d3_uniq" ON "listings_customuser_user_permissions" ("customuser_id", "permission_id");
CREATE INDEX "listings_customuser_user_permissions_customuser_id_298651bb" ON "listings_customuser_user_permissions" ("customuser_id");
CREATE INDEX "listings_customuser_user_permissions_permission_id_447acb0f" ON "listings_customuser_user_permissions" ("permission_id");
CREATE INDEX "listings_listing_host_id_507b665c" ON "listings_listing" ("host_id");
CREATE INDEX "listings_booking_customer_id_48fd750a" ON "listings_booking" ("customer_id");
CREATE INDEX "listings_booking_listing_id_49e4e776" ON "listings_booking" ("listing_id");
CREATE INDEX "listings_review_customer_id_c829889a" ON "listings_review" ("customer_id");
CREATE INDEX "listings_review_listing_id_dc7013f7" ON "listings_review" ("listing_id");
COMMIT;
