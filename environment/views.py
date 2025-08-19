from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import EnvironmentVariable
from .forms import EnvironmentVariableForm
import os


from django.http import HttpResponseForbidden

def check_sudo_permission(view_func):
    """检查是否有sudo权限的装饰器"""
    def wrapper(request, *args, **kwargs):
        # 检查是否有写入系统文件的权限
        test_file = '/etc/environment.test'
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return view_func(request, *args, **kwargs)
        except PermissionError:
            return HttpResponseForbidden("没有足够的权限修改系统环境变量")
    return wrapper


@check_sudo_permission
@login_required
@permission_required('environment.change_environmentvariable', raise_exception=True)
def environment_list(request):
    """环境变量列表（带分页和搜索）"""
    # 从系统加载最新值
    if request.GET.get('refresh'):
        EnvironmentVariable.load_from_system()
        messages.success(request, '已从系统刷新环境变量')
        return redirect('environment:refresh')

    # 获取搜索参数
    search_query = request.GET.get('search', '')

    # 获取所有变量并排序
    if search_query:
        variables_list = EnvironmentVariable.objects.filter(
            key__icontains=search_query
        ).order_by('key')
    else:
        variables_list = EnvironmentVariable.objects.all().order_by('key')

    # 分页设置
    paginator = Paginator(variables_list, 10)  # 每页显示10条
    page = request.GET.get('page')

    try:
        variables = paginator.page(page)
    except PageNotAnInteger:
        variables = paginator.page(1)
    except EmptyPage:
        variables = paginator.page(paginator.num_pages)

    return render(request, 'environment/list.html', {
        'variables': variables,
        'system_env': dict(os.environ),
        'search_query': search_query
    })


@login_required
@permission_required('environment.add_environmentvariable', raise_exception=True)
@csrf_protect
def environment_edit(request, pk=None):
    """编辑环境变量 - 修正版本"""
    if pk:
        variable = get_object_or_404(EnvironmentVariable, pk=pk)
    else:
        variable = None

    if request.method == 'POST':
        form = EnvironmentVariableForm(request.POST, instance=variable)
        if form.is_valid():
            try:
                var = form.save(commit=False)
                scope = form.cleaned_data['scope']
                
                # 应用到系统
                success = var.apply_to_system(scope)
                
                if success or scope == 'session':
                    var.save()
                    messages.success(request, f'环境变量 {var.key} 已{"更新" if pk else "创建"}并应用到{scope}范围')
                    
                    if scope == 'global':
                        messages.info(request, '全局环境变量修改已写入系统文件，部分服务可能需要重启才能生效')
                    
                    return redirect('environment:refresh')
                else:
                    messages.error(request, '应用到系统失败，可能需要sudo权限或检查文件路径')
                    
            except PermissionError as e:
                messages.error(request, f'权限不足: {e}')
            except Exception as e:
                messages.error(request, f'操作失败: {e}')
    else:
        form = EnvironmentVariableForm(instance=variable)

    return render(request, 'environment/edit.html', {
        'form': form,
        'variable': variable
    })


@login_required
@permission_required('environment.delete_environmentvariable', raise_exception=True)
def environment_delete(request, pk):
    """删除环境变量"""
    variable = get_object_or_404(EnvironmentVariable, pk=pk)

    if request.method == 'POST':
        key = variable.key
        variable.delete()

        # 从系统中移除（可选）
        try:
            env_file = '/etc/environment'
            if os.path.exists(env_file) and os.access(env_file, os.W_OK):
                with open(env_file, 'r') as f:
                    lines = f.readlines()

                with open(env_file, 'w') as f:
                    for line in lines:
                        if not line.startswith(f'{key}='):
                            f.write(line)
        except:
            pass

        messages.success(request, f'环境变量 {key} 已删除')
        return redirect('environment:list')

    return render(request, 'environment/delete_confirm.html', {'variable': variable})