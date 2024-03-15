from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class ListingManager(models.Manager):
    def create_listing(self, title, description, category, starting_bid, image_url, user):
        listing = self.create(title=title, description=description, category=category, starting_bid=starting_bid, image_url=image_url, user=user)
        return listing

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    objects = ListingManager()
    
    def __str__(self):
        return f"{self.id}: {self.title} - {self.active}"


class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.id}: {self.amount} - {self.listing}"

class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.id}: {self.text} - {self.listing}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlists")

    def __str__(self):
        return f"{self.id}: {self.user} - {self.listing}"