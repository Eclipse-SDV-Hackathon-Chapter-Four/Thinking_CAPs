/**
 * @kind table
 * Read-only diagnosis: location status of TypedefTypes named in RULE-6-9-1 placeholder results.
 */
import cpp

from TypedefType t, string file, string inst
where
  t.getName() in ["Result", "expected_blank", "FindServiceHandler", "iterator", "MethodInArgPtr",
      "const_iterator", "vector", "TracePointType", "callback", "AccessControl", "value_type"] and
  (if t.getLocation().getFile().getAbsolutePath() != "" then file = "has-file" else file = "no-file") and
  (if t.isFromTemplateInstantiation(_) then inst = "instantiation"
   else if t.isFromUninstantiatedTemplate(_) then inst = "uninstantiated-template"
   else inst = "plain")
select t.getName() as name, file, inst, t.getLocation().toString() as loc
