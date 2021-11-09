<?xml version="1.0"?>  <!-- this is an xml file -->
<!-- Style sheet originally created by Nathan Eaton 2005. -->
<!-- Edited By Andrew Moore  Aug 2006 to wrap text -->

<!-- Sample custom stylesheet created 01/05/2000 by avienneau-->
<!-- KELLY <xsl:stylesheet xmlns:xsl="http://www.w3.org/TR/WD-xsl"> -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">


  <!-- When the root node in the XML is encountered (the metadata element), the  
       HTML template is set up. -->
  <xsl:template match="/">
    <HTML>

    <HEAD>

  <STYLE>
    BODY {font-size:10pt; font-family:Verdana,Arial,sans-serif}
    TD   {font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 9pt; color: #777777}  
    .norm {font-size:10pt; font-family:Verdana,Arial,sans-serif}
  .big   {  font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11pt; color: #333333; font-weight: bold}
  </STYLE>

  
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
          <xsl:value-of select="metadata/idinfo/citation/citeinfo/title"/>
        </DIV>
</TD>
</TR>


</TABLE>
        <BR/>

<hr/>
<BR/>

    <DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
          Citation
        </DIV>
    <BR/>
   

    <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%">

  <!-- Display the title -->
    <TR VALIGN="TOP">
    <TD width="20%"><b><SPAN class="norm">Title:</SPAN></b></TD>
    <TD width ="80%"><font color="#4682B4"><b>
      <SPAN class="norm"><xsl:value-of select="metadata/idinfo/citation/citeinfo/title"/></SPAN></b></font>
    </TD>        
    </TR>

  <!-- Display the origin -->
    <TR VALIGN="TOP">
    <TD width="20%"><b><SPAN class="norm">Custodian:</SPAN></b></TD>
    <TD width ="80%"><font color="#4682B4"><b>
      <SPAN class="norm"><xsl:value-of select="metadata/idinfo/citation/citeinfo/origin"/></SPAN></b></font>
    </TD>        
    </TR>

    </TABLE>
        <BR/><hr/><BR/>
   
        <DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
          Description
        </DIV>
    <BR/>
 

  <!-- Display the abstract -->
    <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%">
    <TR>
          <TD VALIGN="TOP" width="20%">
              <b><SPAN class="norm">Abstract: </SPAN></b>
          </TD>
      <TD width ="80%"><font color="#4682B4"><b>
            <SPAN class="norm"><xsl:value-of select="metadata/idinfo/descript/abstract"/></SPAN></b></font>
        </TD>

    </TR>      
    </TABLE>
      <BR/>

  <!-- Display the Bounding Box -->
  <DIV STYLE="text-decoration:underline; font-size:14; font-weight:bold; color:#000000">
          Geographical Bounding Box
        </DIV>

    <DIV STYLE="margin-left:0.25in">
    <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%">

        <xsl:for-each select="metadata/idinfo/spdom/bounding">
        
    <TR VALIGN="TOP">
      <TD width="10%"><b>North: </b></TD>
      <TD width ="90%"><font color="#4682B4"><b>
    <xsl:value-of select="northbc"/>
      </b></font>
      </TD>
    </TR>

    <TR VALIGN="TOP">
      <TD width="10%"><b>South: </b></TD>
      <TD width ="90%"><font color="#4682B4"><b>
    <xsl:value-of select="southbc"/>
      </b></font>
      </TD>
    </TR>

    <TR VALIGN="TOP">
      <TD width="10%"><b>East: </b></TD>
      <TD width ="90%"><font color="#4682B4"><b>
    <xsl:value-of select="eastbc"/>
      </b></font>
      </TD>
    </TR>

    <TR VALIGN="TOP">
      <TD width="10%"><b>West: </b></TD>
      <TD width ="90%"><font color="#4682B4"><b>
    <xsl:value-of select="westbc"/>
      </b></font>
      </TD>
    </TR>
            </xsl:for-each>
    </TABLE>
        </DIV>
        <BR/><hr/><BR/>


<DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
          Data Currency and Status
        </DIV>
    <BR/>
    <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%">
  
  <!-- Display the Beginning Date -->      
    <TR VALIGN="TOP">
          <TD width="20%"><b><SPAN class="norm">Beginning Date:</SPAN></b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
            <SPAN class="norm"><xsl:value-of select="metadata/idinfo/timeperd/begdate"/></SPAN></b></font>
          </TD>
    </TR>

  <!-- Display the Ending Date -->  
    <TR VALIGN="TOP">
          <TD width="20%"><b><SPAN class="norm">Ending Date:</SPAN></b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
            <SPAN class="norm"><xsl:value-of select="metadata/idinfo/timeperd/enddate[text()]"/></SPAN></b></font>
          </TD>
    </TR>

  <!-- Display the Progress -->
    <TR VALIGN="TOP">
      <TD width="20%"><b>Progress: </b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
          <xsl:value-of select="metadata/idinfo/status/progress"/>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Maintenance/Update -->
    <TR VALIGN="TOP">
      <TD width="20%"><b>Maintenance/Update: </b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
          <xsl:value-of select="metadata/idinfo/status/update"/>
      </b></font>
      </TD>
    </TR>

    </TABLE>
        <BR/><hr/><BR/>

        <DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
          Access
        </DIV>
        
  <!-- Display the Data Format -->        
    <BR/>
    <DIV STYLE="margin-left:0.25in">
    <TABLE BORDER="0" CELLPADDING="0" CELLSPACING="2" width="100%">

    <TR VALIGN="TOP">
      <TD width="20%"><b><SPAN class="norm">Stored Data Format: </SPAN></b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
          <xsl:value-of select="metadata/idinfo/citation/citeinfo/geoform"/>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Coordinate System --> 
    <TR VALIGN="TOP">
        <xsl:if test="metadata/spref/horizsys/cordsysn/projcsn[. != '']">
          <TD width="20%"><b><SPAN class="norm">Projected Coordinate System: </SPAN></b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
            <xsl:value-of select="metadata/spref/horizsys/cordsysn/projcsn"/></b></font>
          </TD>
        </xsl:if>
        
        <xsl:if test="metadata/spref/horizsys/cordsysn/geogcsn[. != '']">
          <TD width="20%"><b><SPAN class="norm">Geographic Coordinate System: </SPAN></b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
            <SPAN class="norm"><xsl:value-of select="metadata/spref/horizsys/cordsysn/geogcsn"/></SPAN></b></font>
          </TD>
        </xsl:if>
    </TR>

  <!-- Display the Access Constraints -->
    <TR VALIGN="TOP">
      <TD width="20%"><b>Access Constraints: </b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
          <SPAN class="norm"><xsl:value-of select="metadata/idinfo/accconst"/></SPAN>
      </b></font>
      </TD>
    </TR>
    </TABLE>
    </DIV>
    <BR/><hr/><BR/>

        <DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
          Data Quality
        </DIV>
        
    <BR/>
    
    
    <DIV STYLE="margin-left:0.25in">
    <TABLE BORDER="0" CELLPADDING="0" CELLSPACING="2" width="100%">

  <!-- Display the Lineage -->
    <TR VALIGN="TOP">
      <TD width="20%"><b>Lineage: </b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
          <SPAN class="norm"><xsl:value-of select="metadata/dataqual/lineage"/> <BR/> </SPAN>
      </b></font>
      </TD>
    </TR>


  <!-- Display the Positional Accuracy -->
    <TR VALIGN="TOP">
      <TD width="20%"><b>Positional Accuracy: </b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
          <SPAN class="norm"><xsl:value-of select="metadata/dataqual/posacc"/></SPAN>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Attribute Accuracy -->
    <TR VALIGN="TOP">
      <TD width="20%"><b>Attribute Accuracy: </b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
          <SPAN class="norm"><xsl:value-of select="metadata/dataqual/attracc"/></SPAN>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Logical Consistency -->
    <TR VALIGN="TOP">
      <TD width="20%"><b><SPAN class="norm">Logical Consistency: </SPAN></b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
          <SPAN class="norm"><xsl:value-of select="metadata/dataqual/logic"/></SPAN>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Completeness -->
    <TR VALIGN="TOP">
      <TD width="20%"><b>Completeness: </b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
          <SPAN class="norm"><xsl:value-of select="metadata/dataqual/complete"/></SPAN>
      </b></font>
      </TD>
    </TR>

    </TABLE>
    </DIV>


    <BR/><hr/><BR/>  

          <DIV>
      <SPAN STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">Attributes List: </SPAN>

          </DIV>
          <BR/>



<DIV STYLE="margin-left:0.25in">
    <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%">
<TR VALIGN="TOP" ALIGN="LEFT">
  
  <!-- Display the Name -->  
  <TH width="20%"><SPAN STYLE="text-decoration:underline; font-weight:bold">Name</SPAN></TH>
  <!-- Display the Description -->    
  <TH width="80%"><SPAN STYLE="text-decoration:underline; font-weight:bold">Description</SPAN></TH>
  
</TR>
</TABLE>
</DIV>

<xsl:for-each select="metadata/eainfo/detailed[attr]">


          <!-- ENTITY NAME. Add a heading with the name of the entity described by 
               the currently selected detailed element. The text "Attributes of:"
               is presented with the heading style; the name is presented with the
               default BODY text. --> 



          <!-- ATTRIBUTES. All attr elements within the current detailed element are 
               selected. The stylesheet loops through them, and for each one applies 
               the attr template, which is defined below. The attr template is 
               analogous to a subroutine in a program. --> 
          <xsl:apply-templates select="attr"/>


          <!-- SEPARATOR. Before looping to the next detailed element, check if the 
               current detailed element is the last in the set using the context 
               element. If it's not the last, add a line and a couple spaces to 
               separate the two attribute lists. The line is created using a centered 
               group of underscore characters. --> 
<!-- KELLY <xsl:if test="context()[not(end())]">
            <DIV CLASS="separator">__________________</DIV>
            <BR/><BR/>
          </xsl:if>
-->
<xsl:if test="position() != last" ><DIV CLASS="separator">__________________</DIV><BR/><BR/></xsl:if>


        </xsl:for-each> <!-- loop to next detailed element --> 

        <BR/><hr/><BR/>

<DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
    Contact Information
</DIV>
    <BR/>
    <DIV STYLE="margin-left:0.25in">
    <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%">

  <!-- Display the Contact Organisation -->  
    <TR VALIGN="TOP">
      <TD width="30%"><b>Contact Organisation: </b></TD>
      <TD width ="70%"><font color="#4682B4"><b>
          <xsl:value-of select="metadata/metainfo/metc/cntinfo/cntorgp/cntorg"/>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Contact Position -->    
    <TR VALIGN="TOP">
      <TD width="30%"><b>Contact Position: </b></TD>
      <TD width ="70%"><font color="#4682B4"><b>
          <xsl:value-of select="metadata/metainfo/metc/cntinfo/cntorgp/cntper"/>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Mail Address -->
    <TR VALIGN="TOP">
      <TD width="30%"><b>Mail Address: </b></TD>
      <TD width ="70%"><font color="#4682B4"><b>
          <xsl:value-of select="metadata/metainfo/metc/cntinfo/cntaddr/addrtype"/>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Suburb/Locality -->
    <TR VALIGN="TOP">
      <TD width="30%"><b>Suburb/Locality: </b></TD>
      <TD width ="70%"><font color="#4682B4"><b>
          <xsl:value-of select="metadata/metainfo/metc/cntinfo/cntaddr/city"/>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Country/State -->
    <TR VALIGN="TOP">
      <TD width="30%"><b>Country/State: </b></TD>
      <TD width ="70%"><font color="#4682B4"><b>
          <xsl:value-of select="metadata/metainfo/metc/cntinfo/cntaddr/state"/>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Postcode -->
    <TR VALIGN="TOP">
      <TD width="30%"><b>Postcode: </b></TD>
      <TD width ="70%"><font color="#4682B4"><b>
          <xsl:value-of select="metadata/metainfo/metc/cntinfo/cntaddr/postal"/>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Telephone -->      
    <TR VALIGN="TOP">
      <TD width="30%"><b>Telephone: </b></TD>
      <TD width ="70%"><font color="#4682B4"><b>
          <xsl:value-of select="metadata/metainfo/metc/cntinfo/cntvoice"/>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Fax -->      
    <TR VALIGN="TOP">
      <TD width="30%"><b>Fax: </b></TD>
      <TD width ="70%"><font color="#4682B4"><b>
          <xsl:value-of select="metadata/distinfo/distrib/cntinfo/cntfax"/>
      </b></font>
      </TD>
    </TR>

  <!-- Display the Email -->      
    <TR VALIGN="TOP">
      <TD width="30%"><b>Email: </b></TD>
      <TD width ="70%"><font color="#4682B4"><b>
          <xsl:value-of select="metadata/distinfo/distrib/cntinfo/cntemail"/>
      </b></font>
      </TD>
    </TR>

        </TABLE>
    </DIV>

        <BR/><hr/><BR/>

<DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
    Metadata Information
</DIV>
    <BR/>
    <DIV STYLE="margin-left:0.25in">
    <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%">

  <!-- Display the Metadata Date -->
    <TR VALIGN="TOP">
          <TD width="20%"><b>Metadata Date: </b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
            <xsl:value-of select="metadata/metainfo/metd/date"/></b></font>
          </TD>
    </TR>

        </TABLE>
    </DIV>

        <BR/><hr/><BR/>

<DIV STYLE="text-decoration:underline; font-size:18; font-weight:bold; color:#000000">
    Additional Metadata
</DIV>
    <BR/>
    <DIV STYLE="margin-left:0.25in">
    <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%">

  <!-- Display the Additional Metadata -->
    <TR VALIGN="TOP">
          <TD width="20%"><b>Additional Metadata: </b></TD>
      <TD width ="80%"><font color="#4682B4"><b>
            <SPAN class="norm"><xsl:value-of select="metadata/metainfo/addmeta"/></SPAN></b></font>
          </TD>
    </TR>

        </TABLE>
    </DIV>

        <BR/><BR/>
      </BODY>

    </HTML>
  </xsl:template>

<xsl:template match="metadata/eainfo/detailed/attr">

    <DIV STYLE="margin-left:0.25in">
    <TABLE BORDER="0" CELLPADDING="3" CELLSPACING="2" width="100%">
    
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
<!-- KELLY <xsl:if test="context()[not(end())]">
      
    </xsl:if>
    -->
	
<xsl:if test="position() != last" ><BR/><BR/></xsl:if>
</TR>
</TABLE>
</DIV>
     
</xsl:template>





</xsl:stylesheet>
