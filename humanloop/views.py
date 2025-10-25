from django.http import HttpResponse
from django.urls import reverse

def api_index(request):
    html = """
    <html>
      <head><title>HumanLoop API Index</title></head>
      <body style="font-family:Arial;padding:20px;">
        <h1>HumanLoop API Dashboard</h1>
        <ul>
          <li><a href="/api/customers/">/api/customers/</a></li>
          <li><a href="/api/supervisors/">/api/supervisors/</a></li>
          <li><a href="/api/requests/">/api/requests/</a></li>
          <li><a href="/api/supervisorresponses/">/api/supervisorresponses/</a></li>
          <li><a href="/api/airesponses/">/api/airesponses/</a></li>
          <li><a href="/api/knowledge-base/">/api/knowledge-base/</a></li>
        </ul>
        <hr/>
        <a href="/">← Back to Chat</a>
      </body>
    </html>
    """
    return HttpResponse(html)
