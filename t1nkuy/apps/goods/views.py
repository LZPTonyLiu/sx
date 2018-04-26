from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins, status
from rest_framework import generics
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle

from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .models import Goods, GoodsCategory, HotSearchWords, Banner
from .filters import GoodsFilter
from .serializers import GoodsSerializer, CategorySerializer, HotWordsSerializer, BannerSerializer
from .serializers import IndexCategorySerializer
# Create your views here.
from rest_framework.generics import ListAPIView

# APIView是比较底层的写法，我们用更加上层的写法代码量会少很多
'''
我们用mixins.ListModeMixin 和 generics.GenericAPIView
来写view
'''
# class GoodsListView(APIView):
#     '''
#     list all goods
#     '''
#     #上面的信息会在接口的descraption字段显示
#     def get(self,request,format = None):
#         goods = Goods.object.all[:10]
#         # manay 处理 多个请求
#         goods_serializer = GoodsSerializer(goods,many=True)
#         return Response(goods_serializer.data)
#
#     def post(self,request,format = None):
#         serializer = GoodsSerializer(data=request.data)
#         if serializer.is_valid():
#             # 使用save函数，会调用serializers.py，里面的create方法
#             serializer.save()
#             return Response(serializer.data,status=status.HTTP_201_CREATED)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
#
'''
1我们用mixins.ListModeMixin 和 generics.GenericAPIView书写
2我们不写get post patch delete这些方法的时候，
就表示这个接口不接受相应的方法请求，在view验证
3在Generics里面有一个listapiview，帮我们继承这两个类,并给出get方法
4在settings里面我们可以设置配置，这事全局配置，我们只需要写修改的字段。
    当然我们可以在view里面自定义配置
    这样接口会增加count next perious result信息这些事GenericAPIview实现
    内容里面url自动拼接域名是restful期中一条
    
'''
# class GoodsListView(mixins.ListModelMixin,generics.GenericAPIView):
class GoodsListView(ListAPIView):
    queryset = Goods.objects.all()[:10]
    # 我们只是设置了serializer_class没有用，我们在下面的list里面嗲用它
    serializer_class = GoodsSerializer
    # 设置了
    pagination_class = GoodsPagination


    # def get(self,request,*args,**kwargs):
    #     # list方法在listModelMixin里面，可以分页，调用serializer，
    #     return self.list(request,*args,**kwargs)
# class GoodsListView(mixins.ListModelMixin,viewsets.GenericViewSet):
#     queryset = Goods.objects.all()
#     serializer_class = GoodsSerializer
#     pagination_class = GoodsPagination
#     # 这个会加上过滤器，然后可以选择filter_fields里面的字段进行过滤
#     # 但是这个是不能够模糊查询的
#     filter_backends = (DjangoFilterBackend,)
#     # 加上filter文件  设置下面字段
#     filter_class =  GoodsFilter
    # filter_fields = ('name','shop_price')
    # # 我们可以重写方法来实现过滤，但是代码量大，drf会有filtering方法来过滤
    # def get_queryset(self):
    #     queryset = Goods.objects.all()
    #     # 0是默认值
    #     price_min = self.request.query_params.get('price_min',0)
    #     if price_min:
    #         queryset = queryset.filter(shop_price_gt = int(price_min))
    #     return queryset

'''

'''
class GoodsPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100


class GoodsListViewSet(CacheResponseMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    商品列表页, 分页， 搜索， 过滤， 排序
    """
    # throttle_classes = (UserRateThrottle, )
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination
    # 这个验证token，
    # authentication_classes = (TokenAuthentication, )
    # 使用都是rest framework的filter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = GoodsFilter
    # t添加相应的字段，会同时搜索三个字段，这个里面还会添加上正则表达式
    # ‘^name’代表 在搜索时候，name字段开头必须以 输入内容为准
    search_fields = ('name', 'goods_brief', 'goods_desc')
    ordering_fields = ('sold_num', 'shop_price')

    # def get(self,request,*args,**kwargs):
    #     '''
    #     这个list方法会自动调用我们的serializer_class方法
    #     把request数据序列化后返回
    #     '''
    #     return self.list(request,*args,**kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
#
# 注释 可以在生成接口文档里面使用
# 这个数据量不大，不使用分页
# 使用retrieveModelMxin 可以来获取商品的详情页
class CategoryViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        商品分类列表数据
    retrieve:
        获取商品分类详情
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer


class HotSearchsViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取热搜词列表
    """
    queryset = HotSearchWords.objects.all().order_by("-index")
    serializer_class = HotWordsSerializer


class BannerViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取轮播图列表
    """
    queryset = Banner.objects.all().order_by("index")
    serializer_class = BannerSerializer


class IndexCategoryViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    首页商品分类数据
    """
    queryset = GoodsCategory.objects.filter(is_tab=True, name__in=["生鲜食品", "酒水饮料"])
    serializer_class = IndexCategorySerializer

