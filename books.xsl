<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <!-- Parameter for the user's reading level -->
  <xsl:param name="userLevel" select="'Intermediate'"/>

  <xsl:template match="/library">
    <html>
      <head>
        <title>Books List</title>
        <style>
          .match { background-color: yellow; }
          .no-match { background-color: green; }
          table { width: 100%; border-collapse: collapse; }
          th, td { border: 1px solid #ccc; padding: 8px; }
        </style>
      </head>
      <body>
        <h1>Books List</h1>
        <table>
          <tr>
            <th>Title</th>
            <th>Themes</th>
          </tr>
          <xsl:for-each select="book">
            <tr>
              <xsl:choose>
                <!-- If the book's level2 equals the userLevel, use the match class -->
                <xsl:when test="readingLevels/level2 = $userLevel">
                  <xsl:attribute name="class">match</xsl:attribute>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:attribute name="class">no-match</xsl:attribute>
                </xsl:otherwise>
              </xsl:choose>
              <td>
                <xsl:value-of select="title"/>
              </td>
              <td>
                <xsl:for-each select="themes/theme">
                  <xsl:value-of select="."/>
                  <xsl:if test="position() != last()">, </xsl:if>
                </xsl:for-each>
              </td>
            </tr>
          </xsl:for-each>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
