# -*- coding: utf-8 -*-
__author__ = 'bobby'

from rest_framework import serializers
from django.db.models import Q

from .models import Goods, GoodsCategory, HotSearchWords, GoodsImage, Banner
from .models import GoodsCategoryBrand, IndexAd
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination


# # 使用serializers.Serializer来设计serializers
# class GoodsSerializer(serializers.Serializer):
#     name = serializers.CharField(required=True,max_length=100)
#     click_num = serializers.IntegerField(default=0)
#     goods_front_Image = serializers.ImageField()
#     def create(self, validated_data):
#
#         return Goods.objects.create(**validated_data)

# 这个model就是指明数据库里是哪张表，fields是指定字段，并且会自动转换为serizlizers字段
# 如果选择了一个外键，我们会把这个外键字段序列化成一个id(数字)
# 在api页面上，右边会有按钮可以通过json方式看返回接口数据
class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"




class CategorySerializer2(serializers.ModelSerializer):
    sub_cat = CategorySerializer3(many=True)
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    # 这个sub_cat是在数据库里面的related_name 这样就可以根据父类反向拿子类
    sub_cat = CategorySerializer2(many=True)
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ("image", )

# 这个可以
class GoodsSerializer(serializers.ModelSerializer):
    # 这个可以把外键的详细信息会潜入到这个接口里面。
    category = CategorySerializer()
    images = GoodsImageSerializer(many=True)
    class Meta:
        model = Goods
        fields = "__all__"




class HotWordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotSearchWords
        fields = "__all__"


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


class IndexCategorySerializer(serializers.ModelSerializer):
    brands = BrandSerializer(many=True)
    goods = serializers.SerializerMethodField()
    sub_cat = CategorySerializer2(many=True)
    ad_goods = serializers.SerializerMethodField()

    def get_ad_goods(self, obj):
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id, )
        if ad_goods:
            good_ins = ad_goods[0].goods
            goods_json = GoodsSerializer(good_ins, many=False, context={'request': self.context['request']}).data
        return goods_json



    def get_goods(self, obj):
        all_goods = Goods.objects.filter(Q(category_id=obj.id)|Q(category__parent_category_id=obj.id)|Q(category__parent_category__parent_category_id=obj.id))
        goods_serializer = GoodsSerializer(all_goods, many=True, context={'request': self.context['request']})
        return goods_serializer.data

    class Meta:
        model = GoodsCategory
        fields = "__all__"
