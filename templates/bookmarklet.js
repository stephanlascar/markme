var description = '';
var referrer = '';
var tags = '';

if (document.selection) {
    description = document.selection.createRange().text
} else if (window.getSelection) {
    description = window.getSelection().toString()
}

if (description.length == 0) {
    var metas = document.getElementsByTagName('meta');
    for (var x = 0, y = metas.length; x < y; x++) {
        if (metas[x].name.toLowerCase() == 'description') {
            description = metas[x].content
        }
    }
}

if (tags.length == 0) {
    var metas = document.getElementsByTagName('meta');
    for (var x = 0, y = metas.length; x < y; x++) {
        if (metas[x].name.toLowerCase() == 'keywords') {
            tags = metas[x].content
        }
    }
}

if (document.referrer) {
    referrer = document.referrer
}

void open('https://radiant-scrubland-4024.herokuapp.com{{url_for("bookmarks.bookmarklet")}}?url=' + encodeURIComponent(location.href) + '&title=' + encodeURIComponent(document.title) + '&description=' + encodeURIComponent(description) + '&tags=' + encodeURIComponent(tags) + '&referrer=' + encodeURIComponent(referrer) + '&public=True', 'mark.me +', 'location=no, toolbar=no, scrollbars=yes, width=430, height=567, status=no');
