// 示例代码。上线前替换为医院正式 HTTPS 域名并完成安全审核。
const API_BASE = "https://hospital.example.com";

function searchNavigation(query) {
  return new Promise((resolve, reject) => {
    if (!query || query.length > 100) {
      reject(new Error("查询内容为空或超过长度限制"));
      return;
    }

    wx.request({
      url: `${API_BASE}/v1/navigation/search`,
      method: "GET",
      data: { q: query },
      timeout: 8000,
      success(response) {
        if (response.statusCode !== 200) {
          reject(new Error("导航服务暂时不可用"));
          return;
        }

        const result = response.data;
        if (result.status === "emergency") {
          wx.showModal({
            title: "请立即就医",
            content: result.message,
            showCancel: false,
            confirmText: "知道了"
          });
        }
        resolve(result);
      },
      fail(error) {
        reject(error);
      }
    });
  });
}

module.exports = { searchNavigation };
