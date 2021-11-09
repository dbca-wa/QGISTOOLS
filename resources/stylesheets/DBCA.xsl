<?xml version="1.0"?>  <!-- this is an xml file -->
<!-- Sample custom stylesheet created 01/05/2000 by avienneau-->
<!-- Style sheet originally created by Nathan Eaton 2005. -->
<!-- Edited By Andrew Moore  Aug 2006 to wrap text -->
<!-- Significant rework to access ArcGIS 10.x metadata performed by Kelly Thomas 2017 -->

<!--
ArcGIS vs QGIS Guide:

    Standard:
        ArcGIS Tools uses .net 3.5 and requires:
            <xsl:stylesheet xmlns:xsl="http://www.w3.org/TR/WD-xsl">
        QGIS Tools uses Qt 4.8 and requires:
            <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    Item Delimeters:
        ArcGIS uses:
            <xsl:if test="context()[not(end())]"> 
                ...            
            </xsl:if>
        QGIS uses 
            <xsl:if test="position() != last" >
                ...
            </xsl:if>
    
    Javascript:
        QGIS will fail if JS single line comments are used
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!-- When the root node in the XML is encountered (the metadata element), the HTML template is set up. -->
<xsl:template match="/">
<HTML>
    <HEAD>
        <title>
            <xsl:value-of select="metadata/idinfo/citation/citeinfo/title"/>
        </title>
        
        <STYLE>
            BODY {font-size:10pt; font-family:Verdana,Arial,sans-serif}
            TD   {font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 9pt; color: #777777}
            .norm {font-size:10pt; font-family:Verdana,Arial,sans-serif}
            .big   {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11pt; color: #333333; font-weight: bold}
        </STYLE>

        <!-- The content from the ArcGIS metadata tooling allows for formmating.
             This formatting is "double escaped" in the xml and the xslt tranlation only allows "single unescaping".
             This javascript uses a legacy version of jquery to perform a second level of unescaping. -->
        <script src="file:///C:/ProgramData/DEC/GIS/jquery-1.12.4.js"></script>
        <script>
            function Trim(text) {
                return text.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
            }

            function UnEscapeHtml() {
                $("span").each(function(index){
                    this.innerHTML = $(this).text();
                });
            }
            
            function FormatDates() {
                $("span.date").each(function(index){
                    var dateString = Trim($(this).text());
                    
                    if (dateString.indexOf("T") == 10) {
                        dateString = dateString.split("T")[0];
                    }
                    
                    if (dateString.length == 8 ) {
                        dateString = dateString.substring(0, 4) + "-" + dateString.substring(4, 6) + "-" + dateString.substring(6, 8)
                    }
                    
                    this.innerHTML = dateString;
                });
            }
            
            function OnLoad(jQuery) {
                UnEscapeHtml();
                FormatDates();
            };
            
            $(OnLoad);
            
        </script>

    </HEAD>

    <!-- The BODY secton defines the content of the HTML page. This page has a 1/4 
         inch margin, a background color, and the default text size used is 13pt. -->
    <BODY STYLE="margin-left:0.25in; margin-right:0.25in; background-color:#FFF8DC; 
                   font-size:13pt">

        <!-- TITLE. The xsl:value-of element selects the title element in the XML 
             file, then places its data inside a DIV element. Because an XSL stylesheet 
             is an XML file, all XSL and HTML elements must be well-formed; that is, 
             they must be properly closed. The /DIV closes the opening division tag. 
             The value-of and break (BR) elements are closed by adding the / at the end. --> 
        <TABLE COLS="2" WIDTH="100%" BGCOLOR="#808040" CELLPADDING="11" BORDER="0" CELLSPACING="0">
            <TR ALIGN="center" VALIGN="center">
                <TD COLSPAN="2">    
                    <DIV STYLE="font-size:30; font-weight:bold; color:#FFFFFF; text-align:center">
                        <xsl:value-of select="/metadata/dataIdInfo/idCitation/resTitle"/>
                        <br/>
                    </DIV>
                </TD>
            </TR>
        </TABLE>
        
        <BR/><hr/><BR/>

        <DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
            Description
        </DIV>
        <BR/>
        <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%" STYLE="margin-left:0.25in">

            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Title:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/idCitation/resTitle"/>
                    </SPAN></b></font>
                </TD>				
            </TR>
            
            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Custodial Organisation:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/idCredit"/>
                    </SPAN></b></font>
                </TD>				
            </TR>

            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Abstract:
                    </SPAN></b></TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/idAbs"/>
                    </SPAN></b></font>
                </TD>				
            </TR>

            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Purpose:
                    </SPAN></b></TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/idPurp"/>
                    </SPAN></b></font>
                </TD>				
            </TR>

            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Tags:
                    </SPAN></b></TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/searchKeys/keyword"/>
                    </SPAN></b></font>
                </TD>				
            </TR>
            
        </TABLE>

        <BR/><hr/><BR/>
        <DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
            Resource Citation
        </DIV>
        <BR/>

        <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%" STYLE="margin-left:0.25in">
            
            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Layer Name:
                    </SPAN></b></TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/idCitation/resAltTitle"/>
                    </SPAN></b></font>
                </TD>				
            </TR>
            
            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Date Created:
                    </SPAN></b></TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm date">
                        <xsl:value-of select="/metadata/dataIdInfo/idCitation/date/createDate"/>
                    </SPAN></b></font>
                </TD>				
            </TR>
            
            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Date Published:
                    </SPAN></b></TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm date">
                        <xsl:value-of select="/metadata/dataIdInfo/idCitation/date/pubDate"/>
                    </SPAN></b></font>
                </TD>				
            </TR>
            
            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Date Revised:
                    </SPAN></b></TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm date">
                        <xsl:value-of select="/metadata/dataIdInfo/idCitation/date/reviseDate"/>
                    </SPAN></b></font>
                </TD>				
            </TR>  

            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Metadata Date:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm date">
                        <xsl:value-of select="/metadata/mdDateSt"/>
                    </SPAN></b></font>
                </TD>
            </TR>

            <xsl:for-each select="/metadata/dataIdInfo/idCitation/citRespParty">
                <xsl:if test="role/RoleCd/@value [.= '002']">
                    <TR VALIGN="TOP">
                        <TD width="20%">
                            <b><SPAN class="norm">
                                Custodial Contact:
                            </SPAN></b></TD>
                        <TD width ="80%">
                            <font color="#4682B4"><b>
                                <SPAN class="norm"><xsl:value-of select="rpIndName"/></SPAN><br/>
                                <SPAN class="norm"><xsl:value-of select="rpPosName"/></SPAN><br/>
                                <SPAN class="norm"><xsl:value-of select="rpOrgName"/></SPAN><br/>
                                <xsl:for-each select="rpCntInfo">
                                    <xsl:for-each select="cntAddress">
                                        <SPAN class="norm"><xsl:value-of select="delPoint"/></SPAN><br/>
                                        <SPAN class="norm" style="text-transform: uppercase;"><xsl:value-of select="city"/></SPAN><xsl:text disable-output-escaping="yes">&amp;nbsp;&amp;nbsp;</xsl:text>
                                        <SPAN class="norm" style="text-transform: uppercase;"><xsl:value-of select="adminArea"/></SPAN><xsl:text disable-output-escaping="yes">&amp;nbsp;&amp;nbsp;</xsl:text>
                                        <SPAN class="norm" style="text-transform: uppercase;"><xsl:value-of select="postCode"/></SPAN><xsl:text disable-output-escaping="yes">&amp;nbsp;&amp;nbsp;</xsl:text>
                                        <SPAN class="norm" style="text-transform: uppercase;">
                                            <xsl:choose>
                                                <xsl:when test="country[.='au']">AUSTRALIA</xsl:when>
                                                <xsl:otherwise><xsl:value-of select="country"/></xsl:otherwise>
                                            </xsl:choose>
                                        </SPAN><br/>
                                        <br/>
                                        <SPAN class="norm">Email: <xsl:value-of select="eMailAdd"/></SPAN><br/>
                                    </xsl:for-each>
                                        <xsl:for-each select="cntPhone">
                                            <SPAN class="norm">Voice: <xsl:value-of select="voiceNum"/></SPAN><br/>
                                            <SPAN class="norm">Fax: <xsl:value-of select="faxNum"/></SPAN><br/>
                                        </xsl:for-each>
                                </xsl:for-each>
                            </b></font>
                        </TD>				
                    </TR>  
                </xsl:if>
            </xsl:for-each>
            
            <xsl:for-each select="/metadata/dataIdInfo/idCitation/citRespParty">
                <xsl:if test="role/RoleCd/@value [.= '005']">
                    <TR VALIGN="TOP">
                        <TD width="20%">
                            <b><SPAN class="norm">
                                Distributor Contact:
                            </SPAN></b></TD>
                        <TD width ="80%">
                            <font color="#4682B4"><b>
                                <SPAN class="norm"><xsl:value-of select="rpIndName"/></SPAN><br/>
                                <SPAN class="norm"><xsl:value-of select="rpPosName"/></SPAN><br/>
                                <SPAN class="norm"><xsl:value-of select="rpOrgName"/></SPAN><br/>
                                <xsl:for-each select="rpCntInfo">
                                    <xsl:for-each select="cntAddress">
                                        <SPAN class="norm"><xsl:value-of select="delPoint"/></SPAN><br/>
                                        <SPAN class="norm" style="text-transform: uppercase;"><xsl:value-of select="city"/></SPAN><xsl:text disable-output-escaping="yes">&amp;nbsp;&amp;nbsp;</xsl:text>
                                        <SPAN class="norm" style="text-transform: uppercase;"><xsl:value-of select="adminArea"/></SPAN><xsl:text disable-output-escaping="yes">&amp;nbsp;&amp;nbsp;</xsl:text>
                                        <SPAN class="norm" style="text-transform: uppercase;"><xsl:value-of select="postCode"/></SPAN><xsl:text disable-output-escaping="yes">&amp;nbsp;&amp;nbsp;</xsl:text>
                                        <SPAN class="norm" style="text-transform: uppercase;">
                                            <xsl:choose>
                                                <xsl:when test="country[.='au']">AUSTRALIA</xsl:when>
                                                <xsl:otherwise><xsl:value-of select="country"/></xsl:otherwise>
                                            </xsl:choose>
                                        </SPAN><br/>
                                        <br/>
                                        <SPAN class="norm">Email: <xsl:value-of select="eMailAdd"/></SPAN><br/>
                                    </xsl:for-each>
                                        <xsl:for-each select="cntPhone">
                                            <SPAN class="norm">Voice: <xsl:value-of select="voiceNum"/></SPAN><br/>
                                            <SPAN class="norm">Fax: <xsl:value-of select="faxNum"/></SPAN><br/>
                                        </xsl:for-each>
                                </xsl:for-each>
                            </b></font>
                        </TD>				
                    </TR>  
                </xsl:if>
            </xsl:for-each>
            
        </TABLE>
        
        <BR/><hr/><BR/>
        <DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
            Details
        </DIV>
        <BR/>

        <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%" STYLE="margin-left:0.25in">

            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Status:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                            <xsl:choose>
                                <xsl:when test="/metadata/dataIdInfo/idStatus/ProgCd/@value[. = '001']">Completed</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/idStatus/ProgCd/@value[. = '002']">Historical Archive</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/idStatus/ProgCd/@value[. = '003']">Obsolete</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/idStatus/ProgCd/@value[. = '004']">On Going</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/idStatus/ProgCd/@value[. = '005']">Planned</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/idStatus/ProgCd/@value[. = '006']">Required</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/idStatus/ProgCd/@value[. = '007']">Under Development</xsl:when>
                                <xsl:otherwise>Empty</xsl:otherwise>
                            </xsl:choose>
                    </SPAN></b></font>
                </TD>
            </TR>

            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Spatial representation type:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:choose>
                            <xsl:when test="/metadata/dataIdInfo/spatRpType/SpatRepTypCd/@value[. = '001']">Vector</xsl:when>
                            <xsl:when test="/metadata/dataIdInfo/spatRpType/SpatRepTypCd/@value[. = '002']">Grid</xsl:when>
                            <xsl:when test="/metadata/dataIdInfo/spatRpType/SpatRepTypCd/@value[. = '003']">Text Table</xsl:when>
                            <xsl:when test="/metadata/dataIdInfo/spatRpType/SpatRepTypCd/@value[. = '004']">Tin</xsl:when>
                            <xsl:when test="/metadata/dataIdInfo/spatRpType/SpatRepTypCd/@value[. = '005']">Stereo Model</xsl:when>
                            <xsl:when test="/metadata/dataIdInfo/spatRpType/SpatRepTypCd/@value[. = '006']">Video</xsl:when>
                            <xsl:otherwise>Empty</xsl:otherwise>
                        </xsl:choose>
                    </SPAN></b></font>
                </TD>
            </TR>
            
             <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Projected Coordinate System:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/Esri/DataProperties/coordRef/projcsn"/>
                    </SPAN></b></font>
                </TD>
            </TR>

            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Geographic Coordinate System:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/Esri/DataProperties/coordRef/geogcsn"/>
                    </SPAN></b></font>
                </TD>
            </TR>
            
            <xsl:for-each select="/metadata/distInfo/distFormat">
                <TR VALIGN="TOP">
                    <TD width="20%">
                        <b><SPAN class="norm">
                            Format Name:
                        </SPAN></b>
                    </TD>
                    <TD width ="80%">
                        <font color="#4682B4"><b><SPAN class="norm">
                            <xsl:value-of select="formatName"/>
                        </SPAN></b></font>
                    </TD>
                </TR>
                <TR VALIGN="TOP">
                    <TD width="20%">
                        <b><SPAN class="norm">
                            Format Version:
                        </SPAN></b>
                    </TD>
                    <TD width ="80%">
                        <font color="#4682B4"><b><SPAN class="norm">
                            <xsl:value-of select="formatVer"/>
                        </SPAN></b></font>
                    </TD>
                </TR>
            </xsl:for-each>
            
            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Scale Resolution:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/dataScale/equScale/rfDenom"/>
                    </SPAN></b></font>
                </TD>
            </TR>
            
            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Distance Resolution:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/dataScale/scaleDist/value"/><xsl:text disable-output-escaping="yes">&amp;nbsp;</xsl:text>
                        <xsl:value-of select="/metadata/dataIdInfo/dataScale/scaleDist/value/@uom"/>
                    </SPAN></b></font>
                </TD>
            </TR>
            
            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Supplemental information:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/suppInfo"/>
                    </SPAN></b></font>
                </TD>
            </TR>
            
            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Access Constraints:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/resConst/Consts/useLimit"/>
                    </SPAN></b></font>
                </TD>
            </TR>

            
        </TABLE>

       
        <BR/><hr/><BR/>
        <DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
            Extents
        </DIV>
        <BR/>

        <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%" STYLE="margin-left:0.25in">

            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Description:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/dataExt/exDesc"/>
                    </SPAN></b></font>
                </TD>
            </TR>
            
            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        North:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/dataExt/geoEle/GeoBndBox/northBL"/>                        
                    </SPAN></b></font>
                </TD>
            </TR>

            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        South:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/dataExt/geoEle/GeoBndBox/southBL"/>
                    </SPAN></b></font>
                </TD>
            </TR>

            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        East:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/dataExt/geoEle/GeoBndBox/eastBL"/>
                    </SPAN></b></font>
                </TD>
            </TR>

            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        West:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dataIdInfo/dataExt/geoEle/GeoBndBox/westBL"/>
                    </SPAN></b></font>
                </TD>
            </TR>
            
        </TABLE>

        
        <BR/><hr/><BR/>
        <DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
            Data Quality
        </DIV>
        <BR/>

        <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%" STYLE="margin-left:0.25in">
        
            <xsl:for-each select="/metadata/dqInfo/report">
                <xsl:choose>
                    <!-- http://support.esri.com/technical-article/000005701 -->
                    <xsl:when test="@type[. = 'DQAbsExtPosAcc']">
                        <TR VALIGN="TOP">
                            <TD width="20%">
                                <b><SPAN class="norm">
                                    Positional Accuracy:
                                </SPAN></b>
                            </TD>
                            <TD width ="80%">
                                <font color="#4682B4"><b><SPAN class="norm">
                                    <xsl:value-of select="measResult/ConResult/conExpl"/>
                                </SPAN></b></font>
                            </TD>
                        </TR>
                    </xsl:when>
                    <xsl:when test="@type[. = 'DQQuanAttAcc']">
                        <TR VALIGN="TOP">
                            <TD width="20%">
                                <b><SPAN class="norm">
                                    Attribute Accuracy:
                                </SPAN></b>
                            </TD>
                            <TD width ="80%">
                                <font color="#4682B4"><b><SPAN class="norm">
                                    <xsl:value-of select="measResult/ConResult/conExpl"/>
                                </SPAN></b></font>
                            </TD>
                        </TR>
                    </xsl:when>
                    <xsl:when test="@type[. = 'DQTopConsis']">
                        <TR VALIGN="TOP">
                            <TD width="20%">
                                <b><SPAN class="norm">
                                    Topological Consistency:
                                </SPAN></b>
                            </TD>
                            <TD width ="80%">
                                <font color="#4682B4"><b><SPAN class="norm">
                                    <xsl:value-of select="measResult/ConResult/conExpl"/>
                                </SPAN></b></font>
                            </TD>
                        </TR>
                    </xsl:when>
                    <xsl:when test="@type[. = 'DQCompComm']">
                        <TR VALIGN="TOP">
                            <TD width="20%">
                                <b><SPAN class="norm">
                                    Completeness:
                                </SPAN></b>
                            </TD>
                            <TD width ="80%">
                                <font color="#4682B4"><b><SPAN class="norm">
                                    <xsl:value-of select="measResult/ConResult/conExpl"/>
                                </SPAN></b></font>
                            </TD>
                        </TR>
                    </xsl:when>

                </xsl:choose>
            </xsl:for-each>
            
            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Lineage:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                        <xsl:value-of select="/metadata/dqInfo/dataLineage/statement"/>
                    </SPAN></b></font>
                </TD>
            </TR>
            
            <TR VALIGN="TOP">
                <TD width="20%">
                    <b><SPAN class="norm">
                        Update frequency:
                    </SPAN></b>
                </TD>
                <TD width ="80%">
                    <font color="#4682B4"><b><SPAN class="norm">
                            <xsl:choose>
                                <xsl:when test="/metadata/dataIdInfo/resMaint/maintFreq/MaintFreqCd/@value[. = '001']">Continual</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/resMaint/maintFreq/MaintFreqCd/@value[. = '002']">Daily</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/resMaint/maintFreq/MaintFreqCd/@value[. = '003']">Weekly</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/resMaint/maintFreq/MaintFreqCd/@value[. = '004']">Fortnightly</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/resMaint/maintFreq/MaintFreqCd/@value[. = '005']">Monthly</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/resMaint/maintFreq/MaintFreqCd/@value[. = '006']">Quarterly</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/resMaint/maintFreq/MaintFreqCd/@value[. = '007']">Biannually</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/resMaint/maintFreq/MaintFreqCd/@value[. = '008']">Annually</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/resMaint/maintFreq/MaintFreqCd/@value[. = '009']">As Needed</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/resMaint/maintFreq/MaintFreqCd/@value[. = '010']">Irregular</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/resMaint/maintFreq/MaintFreqCd/@value[. = '011']">Not Planned</xsl:when>
                                <xsl:when test="/metadata/dataIdInfo/resMaint/maintFreq/MaintFreqCd/@value[. = '012']">Unknown</xsl:when>
                            </xsl:choose>
                    </SPAN></b></font>
                </TD>
            </TR>
        </TABLE>

        <BR/><hr/><BR/>
        <DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
            Attributes
        </DIV>
        <BR/>
        
        
        <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%" STYLE="margin-left:0.25in">
            <TR VALIGN="TOP" ALIGN="LEFT">
                <TH ><SPAN STYLE="text-decoration:underline; font-weight:bold">Name</SPAN></TH>
                <TH ><SPAN STYLE="text-decoration:underline; font-weight:bold">Alias</SPAN></TH>
                <TH ><SPAN STYLE="text-decoration:underline; font-weight:bold">Definition</SPAN></TH>
            </TR>
            <xsl:for-each select="metadata/eainfo/detailed/attr">
                <TR>
                    <TD width="20%">
                        <b><SPAN class="norm">
                            <xsl:value-of select="attrlabl"/>
                        </SPAN></b>
                    </TD>
                    <TD width="20%">
                        <font color="#4682B4"><b><SPAN class="norm">
                            <xsl:value-of select="attalias"/>
                        </SPAN></b></font>
                    </TD>
                    <TD>
                        <font color="#4682B4"><b><SPAN class="norm">
                            <xsl:value-of select="attrdef"/>
                        </SPAN></b></font>
                    </TD>
                </TR>
            </xsl:for-each>
        </TABLE>
        
        <BR/><hr/><BR/>
        <DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
            Additonal Metadata
        </DIV>
        <BR/>

        <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%" STYLE="margin-left:0.25in">
			<xsl:choose>
				<xsl:when test="/metadata/Binary/Enclosure">
					<xsl:for-each select="/metadata/Binary/Enclosure">
						<TR VALIGN="TOP">
							<TD width="20%">
								<b><SPAN class="norm">
									<xsl:value-of select="Data/@OriginalFileName"/>
								</SPAN></b>
							</TD>
							<TD width ="80%">
								<font color="#4682B4"><b><SPAN class="norm">
									<xsl:value-of select="Descript"/>
								</SPAN></b></font>
							</TD>
						</TR>
					</xsl:for-each>
				</xsl:when>
				<xsl:otherwise>
					<TR VALIGN="TOP">
						<TD width="100%">
							<b><SPAN class="norm">
								No additional metadata files. 
							</SPAN></b>
						</TD>
					</TR>
				</xsl:otherwise>
			</xsl:choose> 
		</TABLE>
	</BODY>
</HTML>
</xsl:template>

<xsl:template match="metadata/eainfo/detailed/attr">

	  <DIV STYLE="margin-left:0.25in">
	  <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%" STYLE="margin-left:0.25in">
	  
	<TR VALIGN="TOP">
    <!-- NAME. The attribute name is a heading for the properties listed below. The 
         xsl:choose element tests if there is an attribute name, and if so adds it 
         to the page. Otherwise, the text "Attribute" is added as the heading. --> 
    <xsl:choose>
      <xsl:when test="attrlabl[. != '']">
	  
	    <TD width ="20%"><b>
          <xsl:value-of select="attrlabl"/>
	    </b>
	    </TD>
	  
        
      </xsl:when>
      <xsl:otherwise>
        <DIV CLASS="attribute">Attribute</DIV>
      </xsl:otherwise>
    </xsl:choose>


    <!-- PROPERTIES. For each property, if the tag is present and if it has a value, 
         add a label identifying the property then add its value to the page. --> 


    <xsl:if test="attrdef[. != '']">  
	    <TD width ="80%"><font color="#4682B4"><b>
          <xsl:value-of select="attrdef"/>
	    </b></font>
	    </TD>

    </xsl:if>


    <!-- SPACE. If the current attribute is not the last in the set, add an empty 
         line before the next attribute is added to the page. --> 
    <xsl:if test="position() != last" >
      
    </xsl:if>
</TR>
</TABLE>
</DIV>
     
</xsl:template>





</xsl:stylesheet>