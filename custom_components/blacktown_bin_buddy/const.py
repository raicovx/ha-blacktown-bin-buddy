"""Constants for the bin_buddy integration."""

DOMAIN = "blacktown_bin_buddy"
ADD_SEARCH_URL = "https://www.blacktown.nsw.gov.au/api/v1/myarea/search?keywords="  # append URL encoded search term
WASTE_COLLECTION_DATES_URL = "https://www.blacktown.nsw.gov.au/ocapi/Public/myarea/wasteservices?ocsvclang=en-AU&geolocationid="  # append address GUID - returns html to be parsed

BIN_COLOUR_MAP = {
    "red": "general-waste",
    "yellow": "recycling",
    "green": "food-and-garden-waste",
}
