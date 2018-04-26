# -*- coding: utf-8 -*-
__author__ = 'bobby'

import django_filters
from django.db.models import Q

from .models import Goods

# 这个写rest_framework，打开过滤器的时候才能出现提交按钮
class GoodsFilter(django_filters.rest_framework.FilterSet):
    # looup 是执行的时候，
    price_min = django_filters.NumberFilter(name = 'shop_price',lookup_expr='gte')
    price_max = django_filters.NumberFilter(name = 'shop_price',lookup_expr='lte')
    # name = django_filters.CharFilter(name = 'name', lookup_expr='icontains')

    # Goods.objects.filter(shop_price_gt = )
    class Meta:
        model = Goods
        # fields = ['price_min','price_max','name']
        fields = ['price_min', 'price_max']



class GoodsFilter(django_filters.rest_framework.FilterSet):
    """
    商品的过滤类
    """
    pricemin = django_filters.NumberFilter(name='shop_price', help_text="最低价格",lookup_expr='gte')
    pricemax = django_filters.NumberFilter(name='shop_price', lookup_expr='lte')
    top_category = django_filters.NumberFilter(method='top_category_filter')


    def top_category_filter(self, queryset, name, value):
        return queryset.filter(Q(category_id=value)|Q(category__parent_category_id=value)|Q(category__parent_category__parent_category_id=value))


    class Meta:
        model = Goods
        fields = ['pricemin', 'pricemax', 'is_hot', 'is_new']