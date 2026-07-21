import Document, { Html, Head, Main, NextScript } from 'next/document';

export default class MyDocument extends Document {
  render() {
    return (
      <Html>
        <Head>
          <link rel="preconnect" href="https://ivanintech-backend.onrender.com" />
          <link rel="dns-prefetch" href="https://ivanintech-backend.onrender.com" />
          {/* Añade aquí otros dominios de imágenes o APIs externas si los usas */}
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
} 