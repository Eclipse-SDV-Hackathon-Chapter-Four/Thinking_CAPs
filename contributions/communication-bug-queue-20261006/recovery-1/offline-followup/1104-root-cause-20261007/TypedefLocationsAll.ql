/**
 * @kind table
 */
import cpp

from TypedefType t, Location l
where
  t.getName() in ["Result", "expected_blank", "FindServiceHandler", "iterator", "const_iterator"] and
  l = t.getLocation()
select t.getName() as name, count(t.getLocation()) as nlocs, l.getFile().getAbsolutePath() as file,
  l.getStartLine() as line, l.toString() as loc
