查看商品分类：预计到时候改为游戏，一级目录先不用
http://malldev.huhp.cc/api/mall-admin/productCategory/list/withChildren
入口方法：com.macro.mall.controller.PmsProductCategoryController#listWithChildren
相关表：pms_product_category

商品品牌，预计隐藏，搞个唯一的，以后再搞成对应的公司，如腾讯，网易等
http://malldev.huhp.cc/api/mall-admin/brand/list?pageNum=1&pageSize=100
入口方法：com.macro.mall.controller.PmsBrandController#getList(java.lang.String, java.lang.Integer, java.lang.Integer)
相关表:pms_brand

可以用的规格(SKU)目录
http://malldev.huhp.cc/api/mall-admin/productAttribute/category/list?pageNum=1&pageSize=100
入口方法：com.macro.mall.controller.PmsProductAttributeCategoryController#getList
table:pms_product_attribute_category

pms_sku_stock
pms_product


根据规格id查规格具体的属性，属性应该是充值方式，区服，礼包那些
http://malldev.huhp.cc/api/mall-admin/productAttribute/list/2?pageNum=1&pageSize=100&type=0
入口方法：com.macro.mall.controller.PmsProductAttributeController#getList
table:pms_product_attribute


广告列表就是轮播图
商品分类的页面下“是否显示”选项决定了分类是否展示它

一进入页面就/cart/clear,/cart/add,cart/list拿到cart的id，之后任何操作都是quantity?id=cartId&quantity=n


add的内容是
{"price":200,"productAttr":"[{\"key\":\"充值方式\",\"value\":\"代充\"},{\"key\":\"区服\",\"value\":\"国际服\"},{\"key\":\"产品类型\",\"value\":\"月卡\"}]","productBrand":"暂不可用","productCategoryId":61,"productId":47,"productName":"王者荣耀200元点卡","productPic":"http://huhp-mall-dev.oss-cn-guangzhou.aliyuncs.com/mall-dev/images/20240906/abstract.png","productSkuCode":"202409060047011","productSkuId":285,"productSn":"","productSubTitle":"王者荣耀的200元点卡","quantity":1}


一进来就要clear,add,list了，因为要拿到可用的优惠券信息
/update/quantity
member/coupon/add/33 是用来领取优惠券的

/list/cart/1 是查看当前用户购物车可用的优惠券，每次修改数量后都要重新请求，其中1是指可用的优惠券，是固定的

l/member/coupon/listByProduct/47 是根据产品查看可用的优惠券