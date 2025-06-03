import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const API_BACKEND_URL = import.meta.env.VITE_API_BACKEND_URL;

const ProductDetail = () => {
  const { license_id } = useParams();
  const navigate = useNavigate();

  const [product, setProduct] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

useEffect(() => {
  if (!license_id) return;

  setLoading(true);

  fetch(`${API_BACKEND_URL}/api/production`, {
    credentials: 'include',
  })
    .then((res) => {
      if (!res.ok) throw new Error('無法取得商品資料清單');
      return res.json();
    })
    .then((data: any[]) => {
      console.log(data)
      const foundProduct = data.find(item => String(item.license_id) === String(license_id));
      if (!foundProduct) {
        setError('找不到對應的商品資料');
        setLoading(false);
        return;
      }
      setProduct(foundProduct);
      setLoading(false);
    })
    .catch((err) => {
      setError(err.message || '資料載入失敗');
      setLoading(false);
    });
}, [license_id]);

  const getCardTheme = (licenseName: any) => {
    if (!licenseName) return 'bg-gray-500';
    if (licenseName.includes('基礎')) return 'bg-blue-500';
    if (licenseName.includes('中級')) return 'bg-blue-600';
    if (licenseName.includes('高級')) return 'bg-orange-500';
    return 'bg-gray-500';
  };

  const getDuration = (licenseInfo: any) => {
    if (!licenseInfo || typeof licenseInfo !== 'string') return '3';
    const match = licenseInfo.match(/(\d+)個月/);
    return match ? match[1] : '3';
  };

  const getImageUrl = (picturePath: any) => {
    return `${API_BACKEND_URL}${picturePath}`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-gray-500">載入中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center text-red-600">
        <p>{error}</p>
        <button
          className="mt-6 bg-yellow-400 hover:bg-yellow-500 text-white font-bold py-2 px-4 rounded"
          onClick={() => navigate(-1)}
        >
          返回上一頁
        </button>
      </div>
    );
  }

  if (!product) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 bg-white rounded-lg shadow-md">
      <div className={`${getCardTheme(product.license_name)} text-white p-6 rounded-t-lg`}>
        <h1 className="text-4xl font-extrabold">{product.license_name || '課程名稱'}</h1>
        <p className="mt-2 text-lg opacity-90">官方線上課程</p>
        <div className="mt-4 text-2xl font-bold">
          課程長度: {getDuration(product.license_info)} 個月
        </div>
      </div>

      <div className="mt-6 flex flex-col md:flex-row gap-6">
        <div className="md:w-1/2">
          {product.picture_url ? (
            <img
              src={getImageUrl(product.picture_url)}
              alt={product.license_name || '課程圖片'}
              className="w-full h-auto rounded-md border"
            />
          ) : (
            <div className="w-full h-64 bg-gray-200 rounded-md flex items-center justify-center">
              <span className="text-gray-500 text-sm">暫無圖片</span>
            </div>
          )}
        </div>

        <div className="md:w-1/2">
          <h2 className="text-2xl font-semibold mb-4">商品資訊</h2>
          <p className="mb-2">
            <span className="font-semibold">價格：</span>NT${(product.price || 0).toLocaleString()}
          </p>
          <p className="mb-2">
            <span className="font-semibold">上架日期：</span>{' '}
            {product.created_at ? new Date(product.created_at).toLocaleDateString() : '未知'}
          </p>
          <p className="mb-2">
            <span className="font-semibold">課程說明：</span> {product.description || '無'}
          </p>
          {/* 你可以根據產品物件擴充更多欄位 */}
        </div>
      </div>

      <div className="mt-8 text-center">
        <button
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition"
          onClick={() => navigate(-1)}
        >
          返回上一頁
        </button>
      </div>
    </div>
  );
};

export default ProductDetail;
