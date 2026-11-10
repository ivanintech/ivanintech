import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Términos de Uso | Iván In Tech',
  description:
    'Condiciones de uso del sitio ivanintech.com: acceso, contenidos, propiedad intelectual y responsabilidad.',
};

export default function TerminosUsoPage() {
  return (
    <main className="container mx-auto max-w-3xl px-4 py-16">
      <h1 className="mb-2 text-3xl font-bold">Términos de Uso</h1>
      <p className="mb-10 text-sm text-muted-foreground">Última actualización: 10 de noviembre de 2026</p>

      <div className="space-y-8 text-sm leading-relaxed text-foreground/90">
        <section>
          <h2 className="mb-2 text-lg font-semibold">1. Objeto</h2>
          <p>
            Estos términos regulan el acceso y uso del sitio web <strong>ivanintech.com</strong>,
            un espacio personal de divulgación sobre inteligencia artificial, desarrollo
            de software y tecnología. El acceso al sitio implica la aceptación de estas
            condiciones.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">2. Uso del sitio</h2>
          <p>Te comprometes a hacer un uso lícito del sitio. En particular, no está permitido:</p>
          <ul className="mt-2 list-disc space-y-1 pl-6">
            <li>Intentar acceder a áreas restringidas sin autorización.</li>
            <li>Introducir código malicioso o realizar acciones que dañen el servicio.</li>
            <li>Extraer contenidos de forma masiva y automatizada sin permiso expreso.</li>
            <li>Suplantar la identidad de otra persona o entidad.</li>
          </ul>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">3. Propiedad intelectual</h2>
          <p>
            Los textos, artículos, código y diseño originales de este sitio son propiedad
            de Iván Castro Martínez, salvo que se indique lo contrario. Puedes citar
            fragmentos indicando la fuente y enlazando al artículo original. No se permite
            la reproducción íntegra con fines comerciales sin autorización escrita.
          </p>
          <p className="mt-2">
            Las marcas, logotipos y contenidos de terceros que aparecen en el sitio
            (por ejemplo, en las secciones de noticias o recursos) pertenecen a sus
            respectivos titulares y se muestran con fines informativos.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">4. Contenidos de terceros</h2>
          <p>
            El sitio puede incluir enlaces y fragmentos de contenido de terceros
            (vídeos, repositorios, artículos). No se asume responsabilidad sobre la
            exactitud ni la disponibilidad de dichos contenidos externos.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">5. Ausencia de garantía</h2>
          <p>
            El contenido se ofrece con carácter informativo y divulgativo. No constituye
            asesoramiento profesional (técnico, legal o financiero). El sitio se
            proporciona «tal cual», sin garantía de disponibilidad ininterrumpida ni de
            ausencia de errores.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">6. Limitación de responsabilidad</h2>
          <p>
            En la medida permitida por la ley, no se asume responsabilidad por daños
            derivados del uso del sitio o de la confianza depositada en sus contenidos.
            Esta limitación no afecta a los derechos que la normativa de consumo reconoce
            a los usuarios.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">7. Modificaciones</h2>
          <p>
            Estos términos pueden actualizarse. La versión vigente es siempre la publicada
            en esta página, con su fecha de última actualización.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold">8. Legislación aplicable</h2>
          <p>
            Estos términos se rigen por la legislación española. Para cualquier
            controversia, las partes se someten a los juzgados y tribunales que
            correspondan conforme a la normativa aplicable en materia de consumidores.
          </p>
        </section>
      </div>
    </main>
  );
}
