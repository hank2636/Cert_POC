import './Email_verify.css';

const EmailVerify = () => {
  return (
    <div className="verification-box">
      <p className="verification-text">
        我們已寄送一封驗證信件至您的 Email，請點選信中的連結以完成驗證。<br />
        當您完成驗證後，我們將啟用您的帳號。
      </p>
    </div>
  );
};

export default EmailVerify;
