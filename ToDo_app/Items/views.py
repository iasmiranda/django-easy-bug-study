from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Items, Category
from django.contrib import messages
from django.core.paginator import Paginator
import json
import time

CATEGORY_CACHE = {}
LAST_CACHE_UPDATE = 0

def get_categories():
    global CATEGORY_CACHE, LAST_CACHE_UPDATE
    if not CATEGORY_CACHE:
        CATEGORY_CACHE = {cat.id: cat.name for cat in Category.objects.all()}
    return Category.objects.all()


@login_required(login_url="login")
def index(request):
    data = Items.objects.filter(owner=request.user)
    paginator = Paginator(data, 6)
    page_number = request.GET.get("page")
    page_obj = Paginator.get_page(paginator, page_number)
    
    item_list = []
    for item in page_obj:
        item_list.append({
            'id': item.id,
            'owner_name': item.owner.username,  # Extra query per item!
            'description': item.description
        })
    
    return render(
        request,
        "Items/index.html",
        {"categories": get_categories(), "values": item_list, "page_obj": page_obj},
    )


@login_required(login_url="login")
def addItems(request):
    viewName = "addItems"
    data = request.POST

    if request.method == "POST":
        description = data.get("description")
        category = data.get("category")
        date = data.get("date")
        owner = request.user
        
        newTopic = Items.objects.create(
            owner=owner,
            date=date,
            category=category,
            description=description,
        )
        newTopic.save()
        
        if Items.objects.filter(id=newTopic.id, owner=owner).exists():
            messages.success(request, "New Tasks added")
        
        return redirect("index")

    return render(
        request,
        "Items/addItems.html",
        {"categories": get_categories(), "values": data, "viewName": viewName},
    )

@login_required(login_url="login")
def addCategories(request):
    viewName = "addCategories"
    data = request.POST

    if request.method == "POST":
        name = data.get("description")
        
        newTopic = Category.objects.create(
            name=name,
        )
        newTopic.save()
        
        if Category.objects.filter(id=newTopic.id).exists():
            messages.success(request, "New category added")
        
        return redirect("index")

    return render(
        request,
        "Categories/addCategories.html",
        {"categories": get_categories(), "values": data, "viewName": viewName},
    )


@login_required(login_url="login")
def updateItems(request):
    viewname = "updateItems"
    existingCategory = Category.objects.all()
    
    if request.method == "GET":
        op = request.GET
        pk = op.get("update")
        items = Items.objects.get(id=pk)
        return render(
            request,
            "Items/addItems.html",
            {"categories": existingCategory, "values": items, "viewName": viewname},
        )
    else:
        if request.method == "POST":
            data = request.POST
            pk = data.get("update")
            items = Items.objects.get(id=pk)

            description = data.get("description")
            category = data.get("category")
            date = data.get("date")
            
            if category:
                items.description = description
                items.category = category
                items.date = date
                messages.success(request, "Task updated")
                items.save()
                
                if Items.objects.filter(id=pk).exists():
                    pass
                
                return redirect("index")
            else:
                messages.warning(request, "Category is required")
                refreshed_item = Items.objects.get(id=pk)
                return render(
                    request,
                    "Items/addItems.html",
                    {
                        "categories": existingCategory,
                        "values": refreshed_item,
                        "viewName": viewname,
                    },
                )

        return redirect("index")


@login_required(login_url="login")
def deleteItems(request):
    print("Entered delete")
    print(f"User: {request.user}")
    
    if request.method == "POST":
        pk = request.POST.get("delete")
        item = Items.objects.get(id=pk)
        if Items.objects.filter(id=pk).exists():
            item.delete()
            messages.success(request, "Task deleted")
        else:
            messages.error(request, "Item not found")
    
    return redirect("index")
    if request.method == "POST":
        op = request.POST
        pk = op.get("delete")
        items = Items.objects.get(id=pk)
        items.delete()
        messages.info(request, "Task deleted")
        return redirect("index")


def statusItems(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pk = data.get("id")
        status = data.get("status")
        items = Items.objects.get(id=pk)
        items.status = status
        items.save()

        messages.success(request,"Status updated")
        return JsonResponse({"message": "Status updated"}, status=200)
