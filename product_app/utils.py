from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from order_app.models import WishlistItem
import logging

logger = logging.getLogger(__name__)

def notify_users(product):
    logger.info(f"Notifying users about product availability: {product.name}")
    channel_layer = get_channel_layer()
    wishlist_items = WishlistItem.objects.filter(product=product)
    for item in wishlist_items:
        user = item.wishlist.user
        logger.info(f"Sending notification to user {user.id}")
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                "type": "send_notification",
                "message": f"The product {product.name} is now available!"
            }
        )