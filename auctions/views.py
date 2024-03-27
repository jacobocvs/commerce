from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms

from .models import User, Listing, Bid, Watchlist, Comment


def index(request):
    
    listings = Listing.objects.filter(active=True).all()
    listings_bids = []

    for listing in listings:
        bids = Bid.objects.filter(listing=listing).order_by('-amount').first()
        listings_bids.append({
            "listing": listing,
            "bids": bids
        })

    return render(request, "auctions/index.html" , {
        "listings_bids": listings_bids,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def createListing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        category = request.POST["category"]
        starting_bid = request.POST["starting_bid"]
        image = request.POST["image_url"]
        user = request.user

        try:
            listing = Listing.objects.create_listing(title, description, category, starting_bid, image, user)
            listing.save()
        except IntegrityError:
            return render(request, "auctions/create_listing.html", {
                "message": "Error creating listing."
            })
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create_listing.html")


@login_required
def add_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = request.user

    try:
        watchlist = Watchlist.objects.create_watchlist(listing, user)
        watchlist.save()
    except IntegrityError:
            return render(request, "auctions/listing.html", {
                "message": "Error adding to watchlist."
            })
    return redirect("watchlist")


@login_required
def watchlist(request):
    user = request.user
    watchlist = Watchlist.objects.filter(user=user).all()

    for watch in watchlist:
        listing = watch.listing
        current_bid = listing.bids.order_by('-amount').first()
        if current_bid:
            watch.current_bid = current_bid.amount
        else:
            watch.current_bid = listing.starting_bid

    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist,
    })


@login_required
def remove_from_watchlist(request, watch_id):
    user = request.user
    remove_watch = Watchlist.objects.filter(user=user, id=watch_id)
    remove_watch.delete()
    return redirect("watchlist")


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        listing = self.instance.listing
        if amount <= listing.starting_bid:
            raise forms.ValidationError("Bid must be higher than starting bid.")
        try:
            current_bid = Bid.objects.filter(listing=listing).latest('amount')
            if amount <= current_bid.amount:
                raise forms.ValidationError("Bid must be higher than current bid.")
        except Bid.DoesNotExist:
            pass
        return amount


def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    comments = Comment.objects.filter(listing=listing).all()
    bids = Bid.objects.filter(listing=listing).order_by('-amount')
    bids_counter = bids.count()
    winner = None
    if not listing.active and bids.exists():
        winner = bids.first().user

    context = {
        "listing": listing,
        "comments": comments,
        "bids": bids.first() if bids.exists() else None,
        "bids_counter": bids_counter,
        "winner": winner,
    }

    if request.method == "POST":
        bid = Bid(listing=listing)
        form = BidForm(request.POST, instance=bid)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.user = request.user
            bid.save()
        return redirect('listing', listing_id=listing.id)
    else:
        form = BidForm()

    context["form"] = form
    return render(request, "auctions/listing.html", context)

@login_required
def close_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    listing.active = False
    listing.save()

    try:
        winner = Bid.objects.filter(listing=listing).latest('amount')
        winner = winner.user
    except Bid.DoesNotExist:
        winner = None
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "winner": winner,
    })
