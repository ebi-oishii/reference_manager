from accounts.models import CustomUser

def latest_projects(request):
    # ログインしているユーザーの情報を取得
    if request.user.is_authenticated:
        latest_projects = request.user.projects.order_by("-updated_at")[:5]
        return {"latest_projects": latest_projects}
    return {}