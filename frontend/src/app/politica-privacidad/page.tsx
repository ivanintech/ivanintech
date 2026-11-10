import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Política de Privacidad | Iván In Tech',
  description:
    'Cómo se recogen, usan y protegen tus datos personales en ivanintech.com, conforme al RGPD y la LOPDGDD.',
};

export default function PoliticaPrivacidadPage() {
  return (
    <main className="container mx-auto max-w-3xl px-4 py-16">
      <h1 className="mb-2 text-3xl font-bold">Política de Privacidad</h1>
      <p className="mb-10 text-sm text-muted-foreground">Última actualización: 10 de noviembre de 2026</p>

      <div className="space-y-8 text-sm leading-relaxed text-foreground/90">
        <section>
          <h2 className="mb-2 text-lg font-semibold">1. Responsable del tratamiento</h2>
          <p>
            El responsable del tratamiento de los datos recogidos en este sitio web
            (<strong>ivanintech.com</strong>) es Iván Castro Martínez, con dirección de
            contacto <strong>info@ivanintech.com</strong>.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">2. Datos que se recogen</h2>
          <p>Este sitio puede tratar las siguientes categorías de datos:</p>
          <ul className="mt-2 list-disc space-y-1 pl-6">
            <li>
              <strong>Datos de contacto:</strong> nombre, correo electrónico y el mensaje
              que envíes mediante el formulario de contacto.
            </li>
            <li>
              <strong>Datos de cuenta:</strong> si te registras, correo electrónico y datos
              de autenticación gestionados a través de Firebase Authentication.
            </li>
            <li>
              <strong>Datos analíticos:</strong> información técnica agregada sobre el uso
              del sitio (páginas visitadas, dispositivo, ubicación aproximada).
            </li>
          </ul>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">3. Finalidad y base legal</h2>
          <ul className="mt-2 list-disc space-y-1 pl-6">
            <li>
              <strong>Atender tus consultas:</strong> la base legal es tu consentimiento al
              enviar el formulario (art. 6.1.a RGPD).
            </li>
            <li>
              <strong>Gestionar tu cuenta y el acceso a recursos:</strong> base legal de
              ejecución de la relación contractual (art. 6.1.b RGPD).
            </li>
            <li>
              <strong>Mejorar el sitio mediante estadísticas agregadas:</strong> base legal
              del interés legítimo (art. 6.1.f RGPD), sin perfilado publicitario.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">4. Conservación de los datos</h2>
          <p>
            Los datos de contacto se conservan el tiempo necesario para atender tu
            consulta y, después, durante los plazos legalmente exigibles. Los datos de
            cuenta se conservan mientras la cuenta permanezca activa.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">5. Destinatarios</h2>
          <p>
            No se ceden datos a terceros salvo obligación legal. Se utilizan proveedores
            tecnológicos que actúan como encargados del tratamiento, con las garantías
            del art. 28 RGPD:
          </p>
          <ul className="mt-2 list-disc space-y-1 pl-6">
            <li>Google Firebase (autenticación y base de datos).</li>
            <li>Render y Neon (alojamiento de la aplicación y la base de datos).</li>
            <li>Proveedores de correo electrónico para el envío de respuestas.</li>
          </ul>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">6. Tus derechos</h2>
          <p>
            Puedes ejercer los derechos de acceso, rectificación, supresión,
            limitación, portabilidad y oposición escribiendo a{' '}
            <strong>info@ivanintech.com</strong>, indicando el derecho que deseas ejercer.
            También puedes reclamar ante la Agencia Española de Protección de Datos
            (<a className="underline" href="https://www.aepd.es" rel="noopener noreferrer" target="_blank">www.aepd.es</a>).
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">7. Cookies</h2>
          <p>
            Este sitio utiliza cookies técnicas necesarias para el funcionamiento de la
            autenticación y de la sesión. No se utilizan cookies de publicidad ni de
            seguimiento de terceros con fines comerciales.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">8. Cambios en esta política</h2>
          <p>
            Esta política puede actualizarse para reflejar cambios normativos o técnicos.
            La fecha de última actualización aparece al inicio de esta página.
          </p>
        </section>
      </div>
    </main>
  );
}
