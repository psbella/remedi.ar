<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:sm="http://www.sitemaps.org/schemas/sitemap/0.9">
<xsl:output method="html" encoding="UTF-8" indent="yes" doctype-system="about:legacy-compat"/>

<xsl:template match="/">
<html lang="es">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Sitemap - remedi.ar</title>
    <meta name="robots" content="noindex, follow"/>
    <link rel="stylesheet" href="/style.css"/>
    <link rel="icon" type="image/svg+xml" href="/img/favicon.svg"/>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="header-logo-circle">
            <img src="/img/favicon.svg" alt="remedi.ar" width="38" height="38"/>
        </div>
        <div class="header-texto">
            <h1>Sitemap de remedi.ar</h1>
            <p><xsl:value-of select="count(sm:urlset/sm:url)"/> URLs incluidas para indexación</p>
        </div>
    </div>

    <main id="main-content">
        <div class="sitemap-nota">
            Este es el sitemap XML que usan los buscadores para indexar el sitio.
            Para ver el XML sin esta vista, agregá "view-source:" antes de la URL en la barra de direcciones.
        </div>

        <div class="sitemap-tabla-wrapper">
            <table class="sitemap-tabla">
                <thead>
                    <tr>
                        <th>URL</th>
                        <th>Última modificación</th>
                        <th>Frecuencia</th>
                        <th>Prioridad</th>
                    </tr>
                </thead>
                <tbody>
                    <xsl:for-each select="sm:urlset/sm:url">
                        <xsl:sort select="sm:priority" order="descending" data-type="number"/>
                        <tr>
                            <td>
                                <a href="{sm:loc}"><xsl:value-of select="sm:loc"/></a>
                            </td>
                            <td><xsl:value-of select="sm:lastmod"/></td>
                            <td><xsl:value-of select="sm:changefreq"/></td>
                            <td><xsl:value-of select="sm:priority"/></td>
                        </tr>
                    </xsl:for-each>
                </tbody>
            </table>
        </div>
    </main>
</div>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
