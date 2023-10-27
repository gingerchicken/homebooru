import opennsfw2 as nsfw

from booru.models import Post, RatingThreshold, NSFWAutomationRecord

def get_nsfw_probability(media_path : str):
    """Tag media as sfw"""

    # Check if the type is a video
    # TODO make this more effective

    file_type = media_path.split(".")[-1]

    if file_type == "mp4":
        """
        video_path = media_path
        
        # Return two lists giving the elapsed time in seconds and the NSFW probability of each frame
        elapsed_seconds, nsfw_probabilities = nsfw.predict_video_frames(video_path)

        # Get the average of the nsfw probabilities
        average_nsfw_probability = sum(nsfw_probabilities) / len(nsfw_probabilities)

        # Return the average nsfw probability
        return average_nsfw_probability
        """

        # TODO implement video nsfw detection
        return 0.0

    # Handle images
    image_path = media_path

    # Get the nsfw probability
    nsfw_probability = nsfw.predict_images([image_path])

    # Return the nsfw probability
    return nsfw_probability[0]

def perform_automation(post : Post):
    """Gets the automated rating for the given post."""

    # Check if a NSFW automation record already exists
    if NSFWAutomationRecord.objects.filter(post=post).exists():
        # If so, return
        return post.rating
    
    # Get the media path
    media_path = post.get_media_path()

    # Get the NSFW probability
    predicted_rating_score = get_nsfw_probability(media_path)

    # Create a NSFW automation record
    record = NSFWAutomationRecord(post=post, nsfw_probability=predicted_rating_score)
    record.save()

    # Get the current rating
    current_rating = post.rating

    # Get the rating threshold (for the current rating)
    # If it doesn't exist, just use the automatic rating
    current_rating_threshold = RatingThreshold.objects.filter(rating=current_rating)

    # Get the current rating threshold
    current_rating_score = current_rating_threshold.first() if current_rating_threshold.exists() else 0.0

    # Check if the NSFW probability is greater than the current rating threshold
    if predicted_rating_score <= current_rating_score:
        # If so, return the current rating
        return current_rating

    # Get the predicted rating
    predicted_rating = RatingThreshold.get_rating(predicted_rating_score)

    # Return the predicted rating
    return predicted_rating