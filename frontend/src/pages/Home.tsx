import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BACKEND_URL = import.meta.env.VITE_API_BACKEND_URL;

const ProductCard = ({ product }: any) => {
  const navigate = useNavigate();

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

  // 點擊跳轉處理
  const handleClick = () => {
    navigate(`/productDetail`);
  };

  return (
    <div
      className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300 cursor-pointer"
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === 'Enter') handleClick(); }}
    >
      {/* 頂部彩色區塊 */}
      <div className={`${getCardTheme(product.license_name)} text-white p-4 relative`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold mb-1">{product.license_name || '課程名稱'}</h3>
            <div className="text-sm opacity-90">官方線上課程</div>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{getDuration(product.license_info)}</div>
            <div className="text-sm">個月</div>
          </div>
        </div>

        <div className="mt-2">
          <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
            {(product.license_info && product.license_info.split(' ')[0]) || '課程'}
          </span>
        </div>
      </div>

      {/* 底部資訊區塊 */}
      <div className="p-4">
        <div className="text-center mb-3">
          <div className="text-gray-600 text-sm mb-1">課程圖片</div>

          <div className="flex justify-center">
            {product.picture_url ? (
              <img
                src={getImageUrl(product.picture_url)}
                alt={product.license_name || '課程圖片'}
                className="max-w-full h-32 object-cover rounded-md border"
                onLoad={() => {
                  console.log('圖片載入成功:', getImageUrl(product.picture_url));
                }}
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  console.log('圖片載入失敗:', getImageUrl(product.picture_url));
                  target.style.display = 'none';
                  if (target.nextSibling instanceof HTMLElement) {
                    target.nextSibling.style.display = 'block';
                  }
                }}
              />
            ) : (
              <div className="w-full h-32 bg-gray-200 rounded-md flex items-center justify-center">
                <span className="text-gray-500 text-sm">暫無圖片</span>
              </div>
            )}
            <div className="w-full h-32 bg-gray-200 rounded-md flex items-center justify-center" style={{ display: 'none' }}>
              <span className="text-gray-500 text-sm">圖片載入失敗</span>
            </div>
          </div>
        </div>

        <div className="border-t pt-3">
          <div className="flex justify-between items-center">
            <div className="text-2xl font-bold text-gray-800">NT${(product.price || 0).toLocaleString()}</div>
            <div className="text-xs text-gray-500">{product.created_at ? new Date(product.created_at).toLocaleDateString() : ''}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ProductGrid = ({ products }: any) => (
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    {products.length === 0 ? (
      <div className="col-span-full text-center py-12">
        <div className="text-gray-500 text-lg">尚無商品資料</div>
      </div>
    ) : (
      products.map((product: any) => <ProductCard key={product.license_id} product={product} />)
    )}
  </div>
);

const Home = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BACKEND_URL}/api/production`, {
      credentials: 'include',
    })
      .then((res) => res.json())
      .then((data) => {
        setProducts(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('資料載入失敗:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-gray-500">載入中...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <h2 className="text-3xl font-bold mb-8 text-center text-gray-800">證照課程</h2>
      <ProductGrid products={products} />
    </div>
  );
};

export default Home;
