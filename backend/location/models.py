from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=255)
    alpha2 = models.CharField(max_length=2, default='')
    alpha3 = models.CharField(max_length=3, default='')

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    abbreviation = models.CharField(max_length=2, default='')

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name

class Location(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    zip_code = models.CharField(max_length=10, default='')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.city}, {self.state} {self.zip_code}"
