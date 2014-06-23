<%
_ = mainpage._
fmt = mainpage.toText

%>
        <table class="full_page" id="maintable">
            <thead>
                <tr>
                %for colname in columns:
                    <%
                    colattr = colAttrs.get(colname, dict())
                    %>
                    <th style='${colattr.get("style")}'>${_(colattr.get('name', colname))}</th>
                %endfor
                </tr>
            </thead>
            <tbody>
            %for r in outdata:
                <tr class='${striped.next()}'>
                %for colname in columns:
                    <%
                    colattr = colAttrs.get(colname, dict())
                    %>
                    <td class='${"dtype_%s" % colattr.get("dtype", "T")}' colname='${colname}' style='${colattr.get("style")}'>
                        ${fmt(r[colname], format=colattr.get('format'), mask=colattr.get('mask'), dtype=colattr.get("dtype"))}
                    </td>
                %endfor
                </tr>
            %endfor
            </tbody>
        </table>