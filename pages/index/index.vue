<template>
	<view class="container">
		<!-- 小程序头部兼容 -->
		<!-- #ifdef MP -->
		<!-- <view class="mp-search-box">
			<input class="ser-input" type="text" value="输入关键字搜索" disabled />
		</view> -->
		<!-- #endif -->


		<!-- 头部轮播 -->
		<view class="carousel-section">
			<!-- 标题栏和状态栏占位符 -->
			<view class="titleNview-placing"></view>
			<!-- 背景色区域 -->
			<swiper class="carousel" circular @change="swiperChange">
				<swiper-item v-for="(item, index) in advertiseList" :key="index" class="carousel-item"
					@click="navToAdvertisePage(item)">
					<image :src="item.pic" mode="aspectFill" />
				</swiper-item>
			</swiper>
			<!-- 自定义swiper指示器 -->
			<view class="swiper-dots">
				<text class="num">{{swiperCurrent+1}}</text>
				<text class="sign">/</text>
				<text class="num">{{swiperLength}}</text>
			</view>
		</view>

		<!-- 游戏列表 -->
		<view class="game-section">
			<view class="game-section-inner">
				<view v-for="(item, index) in gameList" :key="index" class="game-item"
					@click="navToGameDetailPage(item)">

					<image :src="item.icon" class="game-logo" />
					<text class="game-name">{{ item.name }}</text>
				</view>
			</view>
		</view>

		<view class="announcement-section">
			<view class="announcement-header">
				<image src="/static/icons8-speaker-50.png" class="announcement-icon" />
				<text class="announcement-title">交易公告</text>
			</view>
			<view class="announcement-text">安全成交
				<span class="highlight-text">812.5万</span>单，累计服务
				<span class="highlight-text">108.2万</span>用户
			</view>
			<view class="announcement-content" ref="announcementContent">
				<view v-for="(item, index) in visibleAnnouncements" :key="index" class="announcement-item">
					<view class="announcement-text-container">
						<view class="dot"></view>
						<text
							style="white-space: nowrap;overflow: hidden;text-overflow: ellipsis;">{{ item.text }}</text>
						<text class="announcement-time"
							style="white-space: nowrap;overflow: hidden;text-overflow: ellipsis;">{{ item.time }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 底部广告 -->
		<view class="bottom-section">
			<view class="bottom-header">
				<image src="/static/icons8-50.png" class="bottom-icon" />
				<text class="bottom-title">特色服务</text>
				<text class="bottom-title-desc">安全保障，极速发货，免费充值</text>
			</view>
			<view class="bottom-ad-container">
				<view v-for="(item, index) in bottomAdList" :key="index" class="bottom-item"
					@click="navToAdvertisePage(item)">
					<image :src="item.pic" class="bottom-ad-icon" mode="aspectFit" />
				</view>
			</view>
		</view>
		<view style="height: 20px;"></view>

		<view>
			<!-- 遮罩层 -->
			<view class="popup-mask" @click="closePopup" v-if="showPopup && couponList.length>0"></view>

			<!-- 优惠券模态框 -->
			<view class="coupon-popup" v-if="showPopup && couponList.length>0">
				<!-- 关闭按钮 -->
				<view class="close-btn" @click="closePopup">×</view>

				<!-- 标题部分 -->
				<view class="popup-header">
					<text class="popup-title">领取优惠券</text>
					<text class="popup-subtitle">限时优惠，点击领取</text>
				</view>
				<!-- 优惠券部分 -->
				<view class="coupon-list">
					<view class="coupon-item" v-for="(item,index) in couponList">
						<view class="coupon-item-left">
							<text class="coupon-amount">￥{{item.amount}}</text>
							<text class="coupon-original-price">{{item.name}}</text>
							<text class="coupon-description">有效期至{{item.endTime | formatDateTime}}</text>
						</view>
						<view class="coupon-item-right" @click="receiveCoupon(item)">
							<view style="font-size: 20px;">立即领取</view>
						</view>
					</view>

				</view>
			</view>
		</view>

	</view>


</template>

<script>
	import {
		fetchContent,
		fetchRecommendProductList
	} from '@/api/home.js';
	import {
		listCouponCanReceive,
		addMemberCoupon
	} from '@/api/coupon.js';
	import {
		formatDate
	} from '@/utils/date';
	import uniLoadMore from '@/components/uni-load-more/uni-load-more.vue';
	export default {
		components: {
			uniLoadMore
		},
		data() {
			return {
				swiperCurrent: 0,
				swiperLength: 0,
				advertiseList: [],
				gameList: [],
				bottomAdList: [],
				announcements: [{
						text: "用户20***673刚成交PUBG M 34.80元",
						time: "28分钟前"
					},
					{
						text: "用户12***439刚成交了代号弥 315元",
						time: "15分钟前"
					},
					{
						text: "用户14***559刚成交了黄火突击 64.8元",
						time: "13分钟前"
					},
					{
						text: "用户f***f刚成交PUBG M 34.80元",
						time: "28分钟前"
					},
					{
						text: "用户a***a刚成交了代号弥 315元",
						time: "15分钟前"
					},
					{
						text: "用户bb***b刚成交了黄火突击 64.8元",
						time: "13分钟前"
					},
					{
						text: "用户c***c刚成交PUBG M 34.80元",
						time: "28分钟前"
					},
					{
						text: "用户d***d刚成交了代号弥 315元",
						time: "15分钟前"
					},
					{
						text: "用户e***e刚成交了黄火突击 64.8元",
						time: "13分钟前"
					},
				],
				visibleAnnouncements: [],
				currentIndex: 0,
				showPopup: true,
				couponList: []
			};
		},
		onLoad() {
			this.loadData();
			this.fetchCoupon()
		},
		mounted() {
			this.visibleAnnouncements = this.announcements.slice(0, 3); // 初始显示前三个公告
			setInterval(this.scrollAnnouncements, 3000); // 每3秒滚动一次
		},
		filters: {
			formatDateTime(time) {
				if (time == null || time === '') {
					return 'N/A';
				}
				let date = new Date(time);
				date.setDate(date.getDate() - 1); // 减去一天
				return formatDate(date, 'yyyy-MM-dd')
			},
		},
		methods: {
			closePopup() {
				this.showPopup = false;
			},
			receiveCoupon(coupon) {
				addMemberCoupon(coupon.id).then(resp => {
					this.fetchCoupon()
					if (resp.code == 200) {
						uni.showToast({
							title: resp.message,
							icon: 'none',
							mask: true,
							duration: 2000,
						});
					}
				})
			},
			//轮播图切换修改背景色
			swiperChange(e) {
				const index = e.detail.current;
				this.swiperCurrent = index;
			},
			async fetchCoupon() {
				listCouponCanReceive().then(resp => {
					this.couponList = resp.data
					console.log(this.couponList)
				})
			},
			/**
			 * 加载数据
			 */
			async loadData() {
				fetchContent().then(response => {
					console.log("onLoad", response.data);
					this.advertiseList = response.data.advertiseList.filter(ad => ad.type === 1);
					this.bottomAdList = response.data.advertiseList.filter(ad => ad.type === 0).slice(0, 3);
					this.swiperLength = this.advertiseList.length;
					this.gameList = response.data.gameList.slice(0, 9);
					this.gameList.push({
						"id": 0,
						"icon": "/static/tab-cate-current.png",
						"name": "更多游戏"
					})
				});
			},

			navToGameDetailPage(game) {
				uni.setStorage({
					key: 'productSelect',
					data: {
						"fid": game.parentId,
						"sid": game.id,
						'gameName': game.name,
						'gamePic': game.icon
					},
					success: () => {
						uni.switchTab({
							url: '/pages/product/game_product'
						});
					}
				});
			},

			//广告详情页
			navToAdvertisePage(item) {
				let url = item.url;
				uni.navigateTo({
					url: `/pages/advertise/index?url=${url}`
				})
			},

			scrollAnnouncements() {
				this.currentIndex = (this.currentIndex + 1) % this.announcements.length;
				const startIndex = this.currentIndex;
				this.visibleAnnouncements = [
					this.announcements[startIndex],
					this.announcements[(startIndex + 1) % this.announcements.length],
					this.announcements[(startIndex + 2) % this.announcements.length],
				];
			},
		},
		// #ifndef MP
		// 标题栏input搜索框点击
		onNavigationBarSearchInputClicked: async function(e) {
			this.$api.msg('点击了搜索框');
		},
		//点击导航栏 buttons 时触发
		onNavigationBarButtonTap(e) {
			const index = e.index;
			if (index === 0) {
				this.$api.msg('点击了扫描');
			} else if (index === 1) {
				// #ifdef APP-PLUS
				const pages = getCurrentPages();
				const page = pages[pages.length - 1];
				const currentWebview = page.$getAppWebview();
				currentWebview.hideTitleNViewButtonRedDot({
					index
				});
				// #endif
				uni.navigateTo({
					url: '/pages/notice/notice'
				})
			}
		}
		// #endif
	}
</script>

<style lang="scss">
	/* #ifdef MP */
	.mp-search-box {
		position: absolute;
		left: 0;
		top: 30upx;
		z-index: 9999;
		width: 100%;
		padding: 0 80upx;

		.ser-input {
			flex: 1;
			height: 56upx;
			line-height: 56upx;
			text-align: center;
			font-size: 28upx;
			color: $font-color-base;
			border-radius: 20px;
			background: rgba(255, 255, 255, .6);
		}
	}

	page {
		.cate-section {
			position: relative;
			z-index: 5;
			border-radius: 16upx 16upx 0 0;
			margin-top: -20upx;
		}

		.carousel-section {
			padding: 0;

			.titleNview-placing {
				padding-top: 0;
				height: 0;
			}

			.carousel {
				.carousel-item {
					padding: 0;
				}
			}

			.swiper-dots {
				left: 45upx;
				bottom: 40upx;
			}
		}
	}

	/* #endif */


	.container {
		background-color: rgb(235, 243, 250);
		/* 为整个容器添加背景图 */
		background-image: url('/static/bg.png');
		background-size: cover;
		/* 背景图片覆盖整个容器 */
		background-position: top center;
		background-repeat: no-repeat;
		/* 确保背景图能覆盖整个视口高度 */
	}

	page {
		background: #f5f5f5;
	}

	.m-t {
		margin-top: 16upx;
	}

	/* 头部 轮播图 */
	.carousel-section {
		position: relative;
		padding-top: 10px;

		.titleNview-placing {
			height: var(--status-bar-height);
			padding-top: 44px;
			box-sizing: content-box;
		}

		.titleNview-background {
			position: absolute;
			top: 0;
			left: 0;
			width: 100%;
			height: 426upx;
			transition: .4s;
		}
	}

	.carousel {
		width: 100%;
		height: 250upx;

		.carousel-item {
			width: 100%;
			height: 100%;
			padding: 0 28upx;
			overflow: hidden;
		}

		image {
			width: 100%;
			height: 100%;
			border-radius: 10upx;
		}
	}


	.swiper-dots {
		display: flex;
		position: absolute;
		left: 60upx;
		bottom: 15upx;
		width: 72upx;
		height: 36upx;
		background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAABkCAYAAADDhn8LAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTMyIDc5LjE1OTI4NCwgMjAxNi8wNC8xOS0xMzoxMzo0MCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6OTk4MzlBNjE0NjU1MTFFOUExNjRFQ0I3RTQ0NEExQjMiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6OTk4MzlBNjA0NjU1MTFFOUExNjRFQ0I3RTQ0NEExQjMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTcgKFdpbmRvd3MpIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6Q0E3RUNERkE0NjExMTFFOTg5NzI4MTM2Rjg0OUQwOEUiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6Q0E3RUNERkI0NjExMTFFOTg5NzI4MTM2Rjg0OUQwOEUiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz4Gh5BPAAACTUlEQVR42uzcQW7jQAwFUdN306l1uWwNww5kqdsmm6/2MwtVCp8CosQtP9vg/2+/gY+DRAMBgqnjIp2PaCxCLLldpPARRIiFj1yBbMV+cHZh9PURRLQNhY8kgWyL/WDtwujjI8hoE8rKLqb5CDJaRMJHokC6yKgSCR9JAukmokIknCQJpLOIrJFwMsBJELFcKHwM9BFkLBMKFxNcBCHlQ+FhoocgpVwwnv0Xn30QBJGMC0QcaBVJiAMiec/dcwKuL4j1QMsVCXFAJE4s4NQA3K/8Y6DzO4g40P7UcmIBJxbEesCKWBDg8wWxHrAiFgT4fEGsB/CwIhYE+AeBAAdPLOcV8HRmWRDAiQVcO7GcV8CLM8uCAE4sQCDAlHcQ7x+ABQEEAggEEAggEEAggEAAgQACASAQQCCAQACBAAIBBAIIBBAIIBBAIABe4e9iAe/xd7EAJxYgEGDeO4j3EODp/cOCAE4sYMyJ5cwCHs4rCwI4sYBxJ5YzC84rCwKcXxArAuthQYDzC2JF0H49LAhwYUGsCFqvx5EF2T07dMaJBetx4cRyaqFtHJ8EIhK0i8OJBQxcECuCVutxJhCRoE0cZwMRyRcFefa/ffZBVPogePihhyCnbBhcfMFFEFM+DD4m+ghSlgmDkwlOgpAl4+BkkJMgZdk4+EgaSCcpVX7bmY9kgXQQU+1TgE0c+QJZUUz1b2T4SBbIKmJW+3iMj2SBVBWz+leVfCQLpIqYbp8b85EskIxyfIOfK5Sf+wiCRJEsllQ+oqEkQfBxmD8BBgA5hVjXyrBNUQAAAABJRU5ErkJggg==);
		background-size: 100% 100%;

		.num {
			width: 36upx;
			height: 36upx;
			border-radius: 50px;
			font-size: 24upx;
			color: #fff;
			text-align: center;
			line-height: 36upx;
		}

		.sign {
			position: absolute;
			top: 0;
			left: 50%;
			line-height: 36upx;
			font-size: 12upx;
			color: #fff;
			transform: translateX(-50%);
		}
	}

	.game-section {
		display: flex;
		justify-content: center;
		align-items: center;
		widows: 100%;
	}

	.game-section-inner {
		display: grid;
		grid-template-columns: repeat(5, 1fr);
		/* 每行5个 */
		// grid-gap: 14px;
		padding: 10px;
		width: 100%;
	}

	.game-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
		width: 100%;
	}

	.game-logo {
		width: 52px;
		height: 52px;
		border-radius: 10px;
		/* 添加圆角 */
	}

	.game-name {
		margin-top: 4px;
		margin-bottom: 8px;
		font-size: 12px;
		white-space: nowrap;
		/* 禁止换行 */
		overflow: hidden;
		text-overflow: ellipsis;
		/* 文字过长时用省略号代替 */
		width: 50px;
		/* 与item宽度相匹配 */
	}

	.announcement-icon {
		width: 20px;
		height: 20px;
		margin-right: 10px;
	}

	.announcement-section {
		background: linear-gradient(180deg, #fff0da, #ffffff 40%);
		/* 渐变背景色 */
		border-radius: 10px;
		padding: 16px;
		margin: 0px 20upx;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		justify-content: flex-start;
		border: 1px solid #f5f5f5;
		/* 正确的颜色代码和边框样式 */
		height: 210px;
	}

	.announcement-header {
		display: flex;
		align-items: center;
	}

	.announcement-title {
		font-weight: bold;
		font-size: 18px;
		color: #262728;
	}

	.announcement-text {
		white-space: nowrap;
		/* 禁止换行 */
		margin: 18px 0;
		/* 上下margin 20px */
		font-size: 16px;
		/* 默认字体大小 */
		line-height: 1.5;
	}

	.highlight-text {
		font-size: 20px;
		font-weight: 800;
	}

	.announcement-content {
		overflow: hidden;
		height: 80px;
		/* 3个公告项的高度，每个公告项40px */
		width: 100%;
		/* 确保占满宽度 */
	}


	.announcement-item {
		font-size: 14px;
		color: #666;
		margin-bottom: 10px;
		height: 20px;
		/* 每个公告项的高度 */
		display: flex;
		align-items: center;
		justify-content: flex-start;
		/* 确保子项左对齐 */
		width: 100%;
		/* 确保占满宽度 */
	}

	.announcement-text-container {
		display: flex;
		align-items: center;
		justify-content: flex-start;
		/* 确保子项左对齐 */
		width: 100%;
	}

	.dot {
		width: 6px;
		height: 6px;
		background-color: #f5b342;
		/* 黄色 */
		border-radius: 50%;
		margin-right: 8px;
	}

	.announcement-time {
		font-size: 12px;
		color: #999;
		/* 较浅的颜色 */
		margin-left: auto;
		/* 将时间推到右侧 */
	}

	@keyframes scrollUp {
		from {
			transform: translateY(100%);
		}

		to {
			transform: translateY(0);
		}
	}


	.bottom-icon {
		width: 20px;
		height: 20px;
		margin-right: 10px;
	}

	.bottom-section {
		background: linear-gradient(180deg, #ddf0ff, #ffffff 40%);
		/* 渐变背景色 */
		border-radius: 10px;
		padding: 16px;
		margin: 12px 20upx;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		justify-content: flex-start;
		border: 1px solid #f5f5f5;
		/* 正确的颜色代码和边框样式 */
		// height: 190px;
	}

	.bottom-header {
		display: flex;
		align-items: center;
	}

	.bottom-title {
		font-weight: bold;
		font-size: 18px;
		color: #262728;
	}

	.bottom-title-desc {
		font-size: 12px;
		color: #8c8c8c;
		margin-left: 12px;
	}

	.bottom-ad-container {
		display: flex;
		justify-content: space-between;
		flex-direction: row;
		align-items: center;
		text-align: center;
		padding: 0px 0;
		width: 100%;
	}

	.bottom-item {
		border-radius: 10px;
		width: 30%;
		/* 三列布局，宽度设为30% */
	}

	.bottom-ad-icon {
		margin-top: 12px;
		width: 100%;
		height: 120px;

	}

	/* 遮罩层 */
	.popup-mask {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: rgba(0, 0, 0, 0.5);
		z-index: 999;
	}

	/* 模态框 */
	.coupon-popup {
		position: fixed;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 80%;
		max-width: 350px;
		background-color: #fff;
		padding: 20px;
		border-radius: 15px;
		z-index: 1000;
		box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
	}

	/* 关闭按钮 */
	.close-btn {
		position: absolute;
		top: 10px;
		right: 10px;
		font-size: 20px;
		cursor: pointer;
	}

	/* 标题部分 */
	.popup-header {
		display: flex;
		flex-direction: row;
		align-items: flex-end;
		justify-content: space-between;
		margin-bottom: 20px;
		width: 100%;
	}

	.popup-title {
		font-size: 16px;
		font-weight: bold;
	}

	.popup-subtitle {
		font-size: 18px;
		color: #fff;
	}

	/* 优惠券列表 */
	.coupon-list {
		margin-top: 10px;
	}

	.coupon-item {
		background-color: #ff6600;
		margin-bottom: 15px;
		border-radius: 10px;
		position: relative;
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: space-between;
		height: 100px;
		overflow: hidden;
	}

	.coupon-item-left {
		color: white;
		padding: 0 15px;
		display: flex;
		flex-direction: column;
		// align-items: flex-start;
		justify-content: flex-start;
	}

	.coupon-item-right {
		width: 38%;
		height: 100%;
		background-color: #ef1635;
		display: flex;
		flex-direction: row;
		// align-items: flex-start;
		justify-content: center;
		align-items: center;
		color: white;
		font-weight: bolder;
		font-size: 24rpx;

	}

	.coupon-amount {
		font-size: 30px;
		font-weight: bold;
	}



	.coupon-original-price {
		font-size: 12px;
	}

	.coupon-description {
		font-size: 12px;
	}
</style>