from routers.results import get_image_for_md5

result = get_image_for_md5('8a59b1695274495001270a1942b87708')
if result:
    print('图片获取成功')
else:
    print('图片获取失败')
