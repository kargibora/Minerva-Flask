from datetime import datetime
def parse_date(post):
    datePosted = post.get("datePosted", "")
    return datetime.strptime(datePosted, "%d/%m/%Y %H:%M:%S")
