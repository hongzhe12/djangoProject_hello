from django.shortcuts import render

# Create your views here.
# 写一个简单的hello world视图函数
def index(request):
    return render(request, 'app/hello_world.html')