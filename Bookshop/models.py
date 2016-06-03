# coding=utf-8
from django.db import models
from django.contrib.auth.models import AbstractUser
import base64
import random


class BookHotestManager(models.Manager):
    def get_hotest_books(self):
        """
        获取当前最热门的书籍
        :return:
        """
        return super(BookHotestManager, self).get_queryset()[:4]


class BookLatestManager(models.Manager):
    def get_latest_books(self):
        return super(BookLatestManager, self).get_queryset()[:4]


class OrderDecryptManager(models.Manager):
    def get_encrypt_order(self, oid):
        key = base64.b64decode(oid)
        t_oid = int(key[: key.find('|')])
        return super(OrderDecryptManager, self).get_queryset().get(oid=t_oid)


class Book(models.Model):
    """
    书籍类
    """
    bid = models.AutoField(primary_key=True)
    isbn = models.CharField(max_length=100)
    name = models.CharField(max_length=2000, verbose_name=u"书名")
    description = models.CharField(max_length=2000, verbose_name=u"简介")
    publish_date = models.DateField(verbose_name=u"出版日期")
    price = models.FloatField(verbose_name=u"价格")
    publisher = models.CharField(max_length=1000, verbose_name=u"出版商")
    page_number = models.IntegerField(verbose_name=u"页数")
    language = models.CharField(max_length=200, verbose_name=u"语言")
    related_books = models.ManyToManyField("self", null=True , blank=True, verbose_name=u"相关书籍")
    cover_image = models.CharField(max_length=100, verbose_name=u"封面图片")

    objects = models.Manager()
    hotest_objects = BookHotestManager() 
    latest_objects = BookLatestManager() 

    class Meta:
        verbose_name = u"书籍"

    def __unicode__(self):
        return self.name

    def get_header_description(self):
        """
        获取简介 200字以内
        :return:
        """
        rt = self.description
        if len(rt) > 200:
            rt = rt[:200] + '...'
        return rt

    def get_related_books(self):
        """
        获取相关书籍
        :return:
        """
        books = self.related_books.all()
        return random.sample(books, 2)


class Account(AbstractUser):
    """
    账户类
    """
    address = models.TextField(verbose_name=u"地址")
    recommend_books = models.ManyToManyField(Book, related_name='accounts_should_recommend_this_book',
                                             verbose_name=u"推荐书籍")
    shop_cart = models.ManyToManyField(Book, through='ShopCart', through_fields=('aid', 'bid'),
                                       verbose_name=u"购物车")
    comments = models.ManyToManyField(Book, related_name='comments_on_this_book', through='Comment',
                                      through_fields=('aid', 'bid'), verbose_name=u"评论")

    class Meta:
        verbose_name = u"帐户"

    def __unicode__(self):
        return self.username + ' @ ' + self.address

    def get_recommend_books(self):
        """
        获取推荐书籍
        :return:
        """
        orders = self.order_set.all()
        all_related = []
        for order in orders:
            for book in order.books.all():
                all_related.extend(book.related_books.all())
        
        length = 4 if (len(all_related) > 4) else len(all_related)
        return random.sample(all_related, length)

States = (
        ('u', u'未完成'),
        ('p', u'正在进行'),
        ('c', u'已完成')
        )


class Order(models.Model):
    oid = models.AutoField(primary_key=True)
    state = models.CharField(max_length=20, choices=States, verbose_name=u"订单状态")
    aid = models.ForeignKey(Account, verbose_name=u"订单所属用户")
    books = models.ManyToManyField(Book, through='OrderBookRelation', through_fields=('oid', 'bid'),
                                   verbose_name=u"书籍")
    date = models.DateTimeField(verbose_name=u"日期")
    decrypt_objects = OrderDecryptManager()

    class Meta:
        verbose_name = u"订单"
        ordering = ['-date']

    def __unicode__(self):
        return self.get_description()

    def get_id(self):
        return base64.b64encode(str(self.oid) + '|' + str(self.date))

    def get_description(self):
        description = ""
        if len(self.books.all()) == 0:
            description += 'empty'
        else:
            relation = OrderBookRelation.objects.filter(oid=self)
            description += relation[0].bid.name + '*' + str(relation[0].number_of_book)
            for book in relation[1 : ]:
                description += ' + ' + book.bid.name + '*' + str(book.number_of_book)
        return description 

    def get_totalprice(self):
        total_price = 0
        relation = OrderBookRelation.objects.filter(oid=self)
        for book in relation:
            total_price += book.bid.price * book.number_of_book
        return total_price


class OrderBookRelation(models.Model):
    oid = models.ForeignKey(Order, verbose_name=u"订单")
    bid = models.ForeignKey(Book, verbose_name=u"书籍")
    number_of_book = models.IntegerField(verbose_name=u"数量")

    class Meta:
        verbose_name = u"订单&书籍关系"


class ShopCart(models.Model):
    aid = models.ForeignKey(Account, verbose_name=u"用户")
    bid = models.ForeignKey(Book, verbose_name=u"书籍")
    number_of_book = models.IntegerField(verbose_name=u"数量")

    class Meta:
        verbose_name = u"购物车"


class Comment(models.Model):
    bid = models.ForeignKey(Book, verbose_name=u"书籍")
    aid = models.ForeignKey(Account, verbose_name=u"用户")
    content = models.CharField(max_length=2000, verbose_name=u"评论内容")
    date = models.DateTimeField(verbose_name=u"日期")

    class Meta:
        verbose_name = u"评论"

    def get_user_info(self):
        return self.aid.username


    def __unicode__(self):
        return str(self.date)+u"的评论"
