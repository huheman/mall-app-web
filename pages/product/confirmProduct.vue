<template>
	<view class="container">
		<!-- 头 -->
		<view style="height: 12px;"></view>
		<view class="product-title">
			<view class="product-game-info">
				<image class="game-image" :src="gamePic" mode="aspectFill"></image>
				<text class="game-name">{{ fullTitleName }}</text>
			</view>
			<view class="product-game-content">
				<view class="product-game-info">
					<image class="game-product-image" :src="productPic" mode="aspectFill"></image>
					<view class="game-product-info">
						<view>{{productName}}</view>
						<view>¥{{price && price.toFixed(2)}}</view>
					</view>
				</view>
				<view class="counter">
					<button class="btn" :class="{addbtn: quantity>1}" @click="decrement">-</button>
					<text class="count">{{ quantity }}</text>
					<button class="btn addbtn" @click="increment">+</button>
				</view>
			</view>
		</view>
		<!-- 优惠券信息晚点处理 -->
		<view class="coupon-container" @click="toggleMask('show')">
			<view class="coupon-title">🏷️优惠券</view>
			<view class="coupon-text">{{couponTips}}</view>
		</view>
		<view class="attribute-container">
			<view class="game-name" style="font-size: 18px;">填写账户信息</view>
			<view class="attribute-content">
				<view v-for="(item,index) in attribute" class="attribute-content-item">
					<view style="font-size: 18px;">{{item.name}}</view>
					<view>
						<select class="attribute-content-item-unit" v-if="item.inputType === 1" v-model="item.value">
							<option v-for="option in item.inputList.split(',')" :key="option" :value="option">
								{{ option }}
							</option>
						</select>
						<input class="attribute-content-item-unit" v-else type="text" v-model="item.value" />
					</view>
				</view>
			</view>
		</view>

		<!-- 底部提交订单栏 -->
		<view class="bottom-bar">
			<view class="bottom-bar-left">
				<view>合计:</view>
				<view class="bottom-bar-left-price">¥{{total && total.toFixed(2)}}</view>
			</view>
			<view class="bottom-bar-right" @click="confirmOrder">
				<text style="color: white;font-size: 18px;">提交订单</text>
			</view>
		</view>
		
		
		<!-- 优惠券面板 -->
		<view class="mask" :class="maskState===0 ? 'none' : maskState===1 ? 'show' : ''" @click="toggleMask">
			<view class="mask-content" @click.stop.prevent="stopPrevent">
				<!-- 优惠券页面，仿mt -->
				<view class="coupon-item" v-for="(item,index) in couponList" :key="index" @click="selectCoupon(item)">
					<view class="con">
						<view class="left">
							<text class="title">{{item.name}}</text>
							<text class="time">有效期至{{item.endTime | formatDateTime}}</text>
						</view>
						<view class="right">
							<text class="price">{{item.amount}}</text>
							<text>满{{item.minPoint}}可用</text>
						</view>
		
						<view class="circle l"></view>
						<view class="circle r"></view>
					</view>
					<text class="tips">{{item.useType | formatCouponUseType}}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import {
		formatDate
	} from '@/utils/date';
	import {
		fetchProductDetail,

	} from '@/api/product.js';
	import {
		generateConfirmOrder,
		generateOrder
	} from '@/api/order.js';
	import {
		clearCartList,
		addCartItem,
		fetchCartList,
		listCoupon,
		updateQuantity,
	} from '@/api/cart.js'
	export default {
		data() {
			return {
				product: undefined,
				fullTitleName: null,
				quantity: 1,
				skuId: null,
				attribute: [],
				total: undefined,
				coupontDesc: 0,
				price: null,
				gamePic: null,
				productName: null,
				productPic: null,
				productSkuStock: null,
				couponList: [],
				selectedCoupon: null,
				cartId: null,
				maskState:0
			}
		},
		async onLoad(options) {
			let id = options.id;
			// this.options = options,
			this.gamePic = options.gamePic
			this.skuId = options.skuId
			this.gameName = options.gameName


			// 拿到要填写的attribute
			this.loadData(id);
		},
		computed:{
			couponTips(){
				if (this.selectedCoupon) {
					return this.selectedCoupon.name
				}
				if (this.couponList && this.couponList.length >0 ){
					return this.couponList.length+'张可用优惠券'
				}else{
					return '暂无可用优惠券'
				}
			}
		},
		watch: {
			quantity(newVal){
				this.fetchCoupon();
				this.calculateTotal();
			},
			selectedCoupon(newVal){
				this.calculateTotal()
			}
		},
		filters: {
			formatDateTime(time) {
				if (time == null || time === '') {
					return 'N/A';
				}
				let date = new Date(time);
				return formatDate(date, 'yyyy-MM-dd hh:mm:ss')
			},
			formatCouponUseType(useType) {
				if (useType == 0) {
					return "全场通用";
				} else if (useType == 1) {
					return "指定分类商品可用";
				} else if (useType == 2) {
					return "指定商品可用";
				}
				return null;
			},
		},
		methods: {
			stopPrevent() {},
			selectCoupon(coupon) {
				this.selectedCoupon = coupon;
				this.toggleMask();
			},
			//显示优惠券面板
			toggleMask(type) {
				let timer = type === 'show' ? 10 : 300;
				let state = type === 'show' ? 1 : 0;
				this.maskState = 2;
				setTimeout(() => {
					this.maskState = state;
				}, timer)
			},
			fetchCoupon() {
				listCoupon().then(resp => {
					this.couponList = resp.data.map(i=>{return i.coupon})
					console.log(this.couponList)
					if (this.couponList.length > 0) {
						this.selectedCoupon = this.couponList[0]
					}else{
						this.selectedCoupon = null
					}
				})
			},
			confirmOrder() {
				generateConfirmOrder(JSON.stringify([this.cartId])).then(response => {
					let orderParam = {
						payType: 0,
						couponId: this.selectedCoupon && this.selectedCoupon.id,
						cartIds: [this.cartId],
						memberReceiveAddressId: null,
						useIntegration: null
					}
					generateOrder(orderParam).then(response => {
						let orderId = response.data.order.id;
						uni.showModal({
							title: '提示',
							content: '订单创建成功，是否要立即支付？',
							confirmText: '去支付',
							cancelText: '取消',
							success: function(res) {
								if (res.confirm) {
									uni.redirectTo({
										url: `/pages/money/pay?orderId=${orderId}`
									})
								} else if (res.cancel) {
									console.log("cancel")
									uni.redirectTo({
										url: '/pages/order/order?state=0'
									})
								}
							}
						});
					});
				});

			},
			decrement() {
				this.updateCart(this.quantity - 1)
			},
			increment() {
				this.updateCart(this.quantity + 1)
			},
			updateCart(num) {
				if (num < 1) {
					return
				}
				updateQuantity({
					id: this.cartId,
					quantity: num
				}).then(response => {
					this.quantity = num
				});
			},
			calculateTotal() {
				this.total = this.price * this.quantity - (this.selectedCoupon ? this.selectedCoupon.amount : 0)
			},
			loadData(id) {
				fetchProductDetail(id).then(response => {
					this.product = response.data.product;
					this.productName = this.product.name;
					this.productPic = this.product.pic
					this.attribute = response.data.productAttributeList.filter(attr => {
						return attr.type == 1
					})
					this.productSkuStock = response.data.skuStockList.filter(item => {
						return item.id == this.skuId
					})[0]
					this.fullTitleName = this.gameName + "/" + JSON.parse(this.productSkuStock.spData).map(item =>
						item.value).join('/')
					this.price = this.productSkuStock.promotionPrice
					this.calculateTotal()
					// 一进来先清空购物车
					clearCartList().then(resp => {
						let cartItem = {
							price: this.price,
							productAttr: this.productSkuStock.spData,
							productBrand: this.product.brandName,
							productCategoryId: this.product.productCategoryId,
							productId: this.product.id,
							productName: this.product.name,
							productPic: this.product.pic,
							productSkuCode: this.productSkuStock.skuCode,
							productSkuId: this.productSkuStock.id,
							productSn: this.product.productSn,
							productSubTitle: this.product.subTitle,
							quantity: this.quantity
						};
						addCartItem(cartItem).then(response => {
							// 加入了购物车，下一步获取购物车内容
							fetchCartList().then(resp => {
								this.cartId = resp.data[0].id
								// todo: 获取优惠券列表
								this.fetchCoupon();
							})
						});
					})
				});
			}
		}
	}
</script>

<style>
	.coupon-text{
		color: #f7245b;
	}
	.coupon-title {
		font-weight: bolder;
		color: #f7245b;
	}
	.coupon-container{
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: space-between;
		background-color: #fee9ef;
		margin: 24rpx;
		border-radius: 10rpx;
		padding: 24px;
	}
	.container {
		background-color: rgb(243, 249, 254);
		/* 为整个容器添加背景图 */
		/* background-image: url('/static/bg.png'); */
		background-size: cover;
		/* 背景图片覆盖整个容器 */
		background-position: top center;
		background-repeat: no-repeat;
		height: 100vh;
		/* 确保背景图能覆盖整个视口高度 */
	}

	.attribute-container {
		border-radius: 10px;
		padding: 16px;
		background-color: white;
		margin: 34rpx 20upx;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		justify-content: flex-start;
		border: 1px solid #f5f5f5;
	}

	.product-title {
		background: linear-gradient(180deg, #d3e4ff, #ffffff 40%);
		/* 渐变背景色 */
		border-radius: 10px;
		padding: 16px;

		margin: 0 20upx;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		justify-content: flex-start;
		border: 1px solid #f5f5f5;
		/* 正确的颜色代码和边框样式 */
	}

	.product-game-info {
		margin: 12px 2px;
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: center;
		height: 50px;
	}

	.product-game-content {
		display: flex;
		flex-direction: row;
		align-items: flex-end;
		justify-content: space-between;
		width: 100%;
	}

	.counter {
		display: flex;
		flex-direction: row;
		justify-content: center;
		align-items: center;
	}

	.btn {
		width: 30px;
		height: 30px;
		display: flex;
		justify-content: center;
		align-items: center;
		background-color: #f4f5f7;
		border-radius: 6px;
		font-size: 24px;
	}

	.addbtn {
		background-color: #0498f2;
		color: white;
	}

	.count {
		margin: 0 10px;
		font-size: 24px;
		font-weight: bold;
	}

	.game-image {
		width: 44px;
		height: 44px;
		border-radius: 10px;
		margin-right: 15px;
	}

	.game-name {
		font-size: 16px;
		font-weight: bold;
		color: #333;
		flex-grow: 1;
	}

	.game-product-image {
		width: 54px;
		height: 54px;
		border-radius: 10px;
		margin-right: 15px;
	}

	.game-product-info {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		justify-content: space-between;
		height: 100%;
	}

	.attribute-content {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		justify-content: space-between;
		margin-top: 12px;
		width: 100%;
	}

	.attribute-content-item {
		margin: 8px 0;
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: space-between;
		width: 100%;
	}

	.attribute-content-item-unit {
		width: 200px;
		/* 你可以根据需要调整宽度 */
		/* padding: 8px; */
		height: 38px;
		border-radius: 4px;
		background-color: #f4f5f9;
		padding: 0 14px;
	}

	.bottom-bar {
		position: fixed;
		bottom: 24px;
		left: 50%;
		width: 95%;
		transform: translateX(-50%);
		max-width: 400px;
		/* 宽度为父容器宽度 - 左右各14px的边距 */
		height: 66px;
		background-color: white;
		/* 背景为深蓝色 */
		display: flex;
		justify-content: space-between;
		align-items: center;
		z-index: 999;
		/* 保证该元素在最前方 */
		overflow: hidden;
		padding: 12px 24px;
	}

	.bottom-bar-left {
		display: flex;
		flex-direction: row;
		justify-content: flex-start;
		align-items: flex-end;
	}

	.bottom-bar-left-price {
		font-size: 24px;
		font-weight: bold;
		margin: 0 12px;
		color: #f7245b;
	}

	.bottom-bar-right {
		background-color: #0498f2;
		width: 120px;
		height: 100%;
		display: flex;
		flex-direction: row;
		justify-content: center;
		align-items: center;
		border-radius: 6px;
		cursor: pointer;
		/* 使鼠标变成手指样式 */
	}
	
	/* 优惠券面板 */
	.mask {
		display: flex;
		align-items: flex-end;
		position: fixed;
		left: 0;
		top: var(--window-top);
		bottom: 0;
		width: 100%;
		background: rgba(0, 0, 0, 0);
		z-index: 9995;
		transition: .3s;
	
		.mask-content {
			width: 100%;
			min-height: 30vh;
			max-height: 70vh;
			background: #f3f3f3;
			transform: translateY(100%);
			transition: .3s;
			overflow-y: scroll;
		}
	
		&.none {
			display: none;
		}
	
		&.show {
			background: rgba(0, 0, 0, .4);
	
			.mask-content {
				transform: translateY(0);
			}
		}
	}
	
	/* 优惠券列表 */
	.coupon-item {
		display: flex;
		flex-direction: column;
		margin: 20upx 24upx;
		background: #fff;
	
		.con {
			display: flex;
			align-items: center;
			position: relative;
			height: 120upx;
			padding: 0 30upx;
	
			&:after {
				position: absolute;
				left: 0;
				bottom: 0;
				content: '';
				width: 100%;
				height: 0;
				border-bottom: 1px dashed #f3f3f3;
				transform: scaleY(50%);
			}
		}
	
		.left {
			display: flex;
			flex-direction: column;
			justify-content: center;
			flex: 1;
			overflow: hidden;
			height: 100upx;
		}
	
		.title {
			font-size: 32upx;
			color: $font-color-dark;
			margin-bottom: 10upx;
		}
	
		.time {
			font-size: 24upx;
			color: $font-color-light;
		}
	
		.right {
			display: flex;
			flex-direction: column;
			justify-content: center;
			align-items: center;
			font-size: 26upx;
			color: $font-color-base;
			height: 100upx;
		}
	
		.price {
			font-size: 44upx;
			color: $base-color;
	
			&:before {
				content: '￥';
				font-size: 34upx;
			}
		}
	
		.tips {
			font-size: 24upx;
			color: $font-color-light;
			line-height: 60upx;
			padding-left: 30upx;
		}
	
		.circle {
			position: absolute;
			left: -6upx;
			bottom: -10upx;
			z-index: 10;
			width: 20upx;
			height: 20upx;
			background: #f3f3f3;
			border-radius: 100px;
	
			&.r {
				left: auto;
				right: -6upx;
			}
		}
	}
</style>