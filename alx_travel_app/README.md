# Dummy Readme

## Welcome to My Chaos

Hey there! If you stumbled into this repository, please ignore the mess. Things are wild here, and I promise it will look much nicer later. For now, this is my playground where I try to make sense of integrating third-party APIs into Django for the first time.

## What I’ve Been Up To

Today was a rollercoaster. I dove headfirst into payment gateways (shoutout to `Chapa`) and learned how to generate checkout links, initiate payments, and handle all the drama that comes with different payment states: PENDING, PROCESSING, SUCCESS, CANCELLED, and FAILED. Along the way, I built DRF actions for initiating and verifying payments and even got fancy with webhooks,receiving signals from Chapa, validating signatures, and updating bookings automatically. Yes, I fought with HMAC hashing and headers like a true warrior.

## Testing Madness

I did a lot of manual testing using CLI, Postman, and the DRF browsable API. I had to deal with session timeouts, invalid API keys, and “why isn’t this request working” moments that made me question my life choices. But eventually, I got it working! Now I can generate checkout links, verify payments, and even handle webhook callbacks like a semi-professional.

## Code Adventures

Inside the views, there’s an elaborate commented-out version of my ViewSet action. It’s messy, nested with ifs, elifs, and elses, but it shows the full logic flow of how payments are handled. Think of it as a “before refactor” time capsule of my thought process.

## The Big Picture

So yes, things are repetitive, messy, and chaotic, but the goal was simple: get a working flow for payments and webhooks. I’ve learned a ton about DRF, API integration, webhooks, request validation, and payment logic. This repo is basically my learning diary, chaos included.

## Closing Note

If you’re exploring this repo, welcome to my developer chaos! I’ll clean it up and make it prettier later. For now, I’m just trying to survive this week of ALX’s course. Pray for me.