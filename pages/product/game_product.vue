<template>
	<view class="container">
		<!-- 名称 -->
		<view class="game-head">
			<image class="game-image" :src="gamePic" mode="aspectFill"></image>
			<text class="game-name">{{ gameName }}</text>
		</view>


		<view class="game-area">
			<!-- 充值方式 -->
			<view class="tab-bar">
				<view class="tab" :class="{ active: currentChargeType === item }"
					v-for="(item,index) in chargeTypeOptions" :key="index" @click="setTab(item)">{{item}}</view>
			</view>

			<!-- 游戏区服 -->
			<view class=" tab-bar">
				<view class="tab" :class="{ active: currentArea === item }" v-for="(item,index) in areaOptions"
					:key="index" @click="setArea(item)">{{item}}</view>
			</view>

			<!-- 充值礼包 -->
			<view class="grid-container">
				<view class="grid-item" :class="{ 'active-option': item === selectedGift }"
					v-for="(item, index) in giftOptions" :key="index" @click="onGiftClick(item)">
					<view>{{ item }}</view>
				</view>
			</view>

			<!-- Content for each tab -->
			<view>
				<text class="product-info-title">商品详情</text>
			</view>
			<!-- 商品网格展示 -->
			<view class="product-grid">
				<view class="product-item" v-for="(item, index) in productList" :key="index"
					@click="selectPorduct(item)" :class="{ 'active-option': selectedSku&& item.skuId === selectedSku.skuId }">
					<image :src="item.pic" class="product-image" mode="aspectFill"></image>
					<view class="product-item-info">
						<view :class="{ 'active-option': selectedSku&& item.skuId === selectedSku.skuId }" class="product-name">
							{{ item.name }}
						</view>
						<view :class="{ 'active-option': selectedSku&& item.skuId === selectedSku.skuId }" class="product-price">
							¥{{ (item.promotPrice || item.price).toFixed(2) }}</view>
					</view>
				</view>
			</view>
		</view>


		<!-- 底部购买栏 -->
		<view class="bottom-bar" v-if="selectedSku">
			<view class="total-info">
				<view class="price-details">
					<text class="total-label">价格：</text>
					<text class="total-price">¥{{ (selectedSku.promotPrice || selectedSku.price).toFixed(2) }}</text>
					<view class="original-price-container" v-if="selectedSku.promotPrice && selectedSku.price && selectedSku.promotPrice != selectedSku.price">
						<text class="original-price">原价¥{{ selectedSku.price.toFixed(2) }}</text>
						<text class="discount">优惠¥{{ (selectedSku.price - selectedSku.promotPrice).toFixed(2) }}</text>
					</view>
				</view>
			</view>
			<view class="buy-button-back">
				<view class="buy-button" @click="navToDetailPage">立即购买</view>
			</view>
			
		</view>
	</view>


</template>

<script>
	import {
		fetchProductDetailByCategory
	} from '@/api/product.js';
	export default {
		data() {
			return {
				productCategoryId: '',
				gameName: '',
				gamePic: '',
				currentChargeType: undefined, // Default to 港台服
				currentArea: undefined,
				selectedGift: undefined,
				// 产品类型可选项
				giftOptions: [],
				// 游戏区服可选项
				areaOptions: [],
				tree: {},
				chargeTypeOptions: [],
				productList: [],
				selectedSku: undefined
			};
		},
		watch: {
			// 监听 currentChargeType 的变化
			currentChargeType(newVal, oldVal) {
				let areaInfo = this.tree[newVal]
				if (areaInfo) {
					this.areaOptions = Object.keys(areaInfo)
					if (!this.currentArea || (this.currentArea && !this.areaOptions.includes(this.currentArea))) {
						this.currentArea = this.areaOptions[0]
					}
				}
				this.findPorducts()
			},
			currentArea(newVal, oldVal) {
				if (!this.currentChargeType || !newVal) {
					return
				}
				let gift = this.tree[this.currentChargeType][newVal]
				if (!gift || Array.isArray(gift)) {
					this.giftOptions = []
					this.selectedGift = undefined
				} else {
					this.giftOptions = Object.keys(gift)
					if (!this.selectedGift || (this.selectedGift && !this.giftOptions.includes(this.selectedGift))) {
						this.selectedGift = this.giftOptions[0]
					}
				}
				this.findPorducts()
			},
			selectedGift() {
				this.findPorducts()
			}
		},
		onShow() {
			this.selectedSku = undefined
			uni.getStorage({
				key: 'productSelect',
				success: (res) => {
					let productSelect = res.data;
					if (this.productCategoryId == productSelect.sid) {
						return
					}
					this.productCategoryId = productSelect.sid;
					this.gameName = productSelect.gameName
					this.gamePic = productSelect.gamePic
					this.loadData();
				}
			});
		},
		methods: {
			//详情
			navToDetailPage() {
				if(this.selectedSku) {
					uni.navigateTo({
						url: `/pages/product/confirmProduct?id=${this.selectedSku.productId}&gameName=${this.selectedSku.gameName}&gamePic=${this.selectedSku.gamePic}&skuId=${this.selectedSku.skuId}`
					})
				}
				
			},
			selectPorduct(item) {
				this.selectedSku = item
			},
			onGiftClick(selectedGift) {
				this.selectedGift = selectedGift;
			},
			setTab(item) {
				this.currentChargeType = item;
			},
			setArea(item) {
				this.currentArea = item;
			},
			findPorducts() {
				if (this.currentArea && this.currentArea) {
					let l3 = this.tree[this.currentChargeType][this.currentArea]
					if (l3) {
						if (Array.isArray(l3)) {
							this.productList = l3
						} else {
							if (this.selectedGift) {
								this.productList = this.tree[this.currentChargeType][this.currentArea][this.selectedGift]
							}
						}
					}

				}
			},
			loadData(categoryId) {
				this.currentChargeType = undefined
				this.currentArea = undefined
				this.selectedGift = undefined
				this.giftOptions = []
				this.areaOptions = []
				this.tree = {}
				this.chargeTypeOptions = []
				this.productList = []
				this.selectedProduct = undefined
				uni.showLoading({
					title: '请稍后..',
					mask: true,
				})
				fetchProductDetailByCategory(this.productCategoryId)
					.then(resp => {
						resp.data.forEach(item => {
							// 收集item的内容
							// 要根据这几项进行计算，形成一个树状图
							// {'直充':{'国际服':{'100元点卡':[{someProductInfo}}]}}
							item.skuStockList.forEach(skuStock => {
								let spData = JSON.parse(skuStock.spData)
								let currentTree = this.tree;
								for (let i = 0; i < spData.length; i++) {
									if (i == spData.length - 1) {
										let currentList = currentTree[spData[i].value] || []
										if (!currentList.includes(item => {
												return item.productId == skuStock.productId
											})) {
											currentList.push({
												'productId': skuStock.productId,
												'skuCode': skuStock.skuCode,
												'price': skuStock.price,
												'skuId': skuStock.id,
												'pic': item.product.pic,
												'name': item.product.name,
												'promotPrice':skuStock.promotionPrice,
												'gameName': this.gameName,
												'gamePic': this.gamePic,
												'spData':spData,
												'productBrand':item.brand.name,
												'productCategoryId':this.productCategoryId,
												'productSubTitle':item.product.subTitle
												
											})
										}

										currentTree[spData[i].value] = currentList

									} else if (!currentTree[spData[i].value]) {
										currentTree[spData[i].value] = {}
										currentTree = currentTree[spData[i].value]
									} else {
										currentTree = currentTree[spData[i].value]
									}
								}
							})
						})
						this.chargeTypeOptions = Object.keys(this.tree)
						this.currentChargeType = this.chargeTypeOptions[0]
						uni.hideLoading();
					})

			}
		}
	}
</script>

<style>
	.container {
		background-color: rgb(235, 243, 250);
		/* 为整个容器添加背景图 */
		background-image: url('/static/bg.png');
		background-size: cover;
		/* 背景图片覆盖整个容器 */
		background-position: center;
		background-repeat: no-repeat;
		height: 800px;
		/* 确保背景图能覆盖整个视口高度 */
		position: relative;
		/* 让子元素的 fixed 位置基于父容器 */
		width: 100%;
		/* 确保父容器的宽度为 100% */
		
	}

	.game-head {
		display: flex;
		align-items: center;
		padding: 10px;
	}

	.game-image {
		width: 80px;
		height: 80px;
		border-radius: 10px;
		margin-right: 15px;
	}

	.game-name {
		font-size: 18px;
		font-weight: bold;
		color: #333;
		flex-grow: 1;
	}

	.tab-bar {
		display: flex;
		justify-content: space-around;
	}

	.tab {
		padding: 15px;
		font-size: 16px;
		color: #333;
	}

	.tab.active {
		color: #ff0000;
		font-weight: bold;
		border-bottom: 2px solid #ff0000;
	}

	.grid-container {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		padding: 12px;
	}

	.grid-item {
		width: 30%;
		text-align: center;
		background-color: #f8f8f9;
		border-radius: 4px;
		margin-bottom: 10px;
		padding: 8px;
		font-size: 14px;
	}

	.active-option {
		background-color: #ebf7fe;
		color: #0592ed !important;
	}

	.product-info-title {
		font-size: 18px;
		font-weight: bold;
		color: #333;
		margin: 10px;
	}

	.product-grid {
		margin-top: 20px;
		display: flex;
		flex-wrap: wrap;
		justify-content: flex-start;
		padding: 0 10px;
	}

	.product-item {
		width: 30%;
		/* 每个商品占30%的宽度 */
		/* background-color: #fff; */
		border: 1px solid #ddd;
		border-radius: 10px;
		text-align: center;
		margin-bottom: 15px;
		margin-right: 10px;
		/* 每个商品右侧有间距，保证左对齐 */
		/* height: 210px; */
	}

	.product-item-info {
		padding: 10px;
		height: 76px;
		border-radius: 0 0 10px 10px;
	}

	.product-image {
		width: 100%;
		height: 128px;
		object-fit: contain;
		border-radius: 10px 10px 0 0;
	}

	.product-name {
		font-size: 13px;
		color: #333;
		margin-bottom: 5px;
		height: 30px;
		white-space: nowrap;
		/* 禁止换行 */
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.product-price {
		font-size: 16px;
		color: #ff0000;
	}

	/* 底部购买栏 */
	.bottom-bar {
		position: fixed;
		bottom: 64px;
		left: 50%;
		width: 95%;
		transform: translateX(-50%);
		max-width: 400px;
		/* 宽度为父容器宽度 - 左右各14px的边距 */
		height: 56px;
		background: linear-gradient(90deg, #233d81, #284eac);
		/* 背景为深蓝色 */
		display: flex;
		justify-content: space-between;
		align-items: center;
		z-index: 999;
		border-radius: 10px;
		/* 保证该元素在最前方 */
		overflow: hidden;
	}

	/* 立即购买按钮 */
	.buy-button-back {
		background: linear-gradient(90deg, #0599f3, #16bbfd);
		height: 100%;
		width: 120px;
		position: absolute;
		right: 0;
		border-radius: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;    /* 垂直方向居中 */
	}
	.buy-button {
		color: white;
		font-size: 18px;

	}

	/* 合计信息部分 */
	.price-details {
		display: flex;
		flex-direction: row;
		align-items: center;
		color: white;
		
	}

	.total-label {
		margin-left: 14px;
		font-size: 16px;
		color: #fff;
	}

	.total-price {
		font-size: 24px;
		font-weight: bold;
		color: #ff4066;
	}

	.original-price-container {
		display: flex;
		flex-direction: column;
		align-items: left;
		margin-left: 12px;
	}

	.original-price {
		font-size: 12px;
		color: #ccc;
		text-decoration: line-through;
		margin-right: 5px;
	}

	.discount {
		font-size: 12px;
		color: #f72d5c;
	}
</style>