from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.createListing, name="createListing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/<int:listing_id>/add_watchlist", views.add_watchlist, name="add_watchlist"),
    path('watchlist/remove/<int:watch_id>', views.remove_from_watchlist, name='remove_from_watchlist'),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<int:listing_id>/place_bid", views.place_bid, name="place_bid"),
    path("listing/<int:listing_id>/close_listing", views.close_listing, name="close_listing"),
]
