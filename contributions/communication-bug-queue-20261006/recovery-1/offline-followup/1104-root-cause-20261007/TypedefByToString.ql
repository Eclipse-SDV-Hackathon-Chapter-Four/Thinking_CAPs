/**
 * @kind table
 */
import cpp

from TypedefType t, string inst
where
  t.toString() in ["Result", "expected_blank", "FindServiceHandler", "iterator"] and
  (if t.isFromTemplateInstantiation(_) then inst = "instantiation"
   else if t.isFromUninstantiatedTemplate(_) then inst = "uninstantiated-template"
   else inst = "plain")
select t.toString() as label, t.getName() as name, count(t.getLocation()) as nlocs,
  count(t.getADeclarationEntry()) as ndecls, inst, t.getBaseType().toString() as base,
  concat(t.getLocation().toString(), ";") as locs
