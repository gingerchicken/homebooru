from django.db import models

class TagType(models.Model):
    # We will use the type name as the primary key
    name = models.CharField(max_length=100, primary_key=True)

    # Description of the tag type
    description = models.CharField(max_length=1000, blank=True, null=True)

class Tag(models.Model):
    # We will use the tag name as the primary key
    tag = models.CharField(max_length=100, primary_key=True)

    # Tag type as a foreign key to the TagType model
    tag_type = models.ForeignKey(TagType, on_delete=models.CASCADE, null=True, blank=True)
