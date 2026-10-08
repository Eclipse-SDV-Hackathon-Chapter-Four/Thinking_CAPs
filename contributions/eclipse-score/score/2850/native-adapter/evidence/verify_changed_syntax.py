# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

from pathlib import Path
import ast,json,re
import yaml
r=Path(__file__).resolve().parent;n=r/'draft-native';paths=json.loads((r/'changed-files.json').read_text());sizes=[]
def object_pairs(pairs):
 out={}
 for key,value in pairs:
  if key in out:raise ValueError('duplicate JSON key')
  out[key]=value
 return out
for relative in paths:
 p=n/relative;raw=p.read_bytes();text=raw.decode('utf-8')
 assert raw.endswith(b'\n') and not raw.endswith(b'\n\n'),relative
 assert '\r' not in text and not any(line.rstrip()!=line for line in text.splitlines()),relative
 assert not re.search(r'^<<<<<<< |^>>>>>>> |^=======$',text,re.M),relative
 assert not re.search(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',text),relative
 assert len(raw)<=150*1024,relative
 if p.suffix=='.json':json.loads(text,object_pairs_hook=object_pairs)
 if p.suffix=='.py':ast.parse(text,filename=relative)
 if p.suffix in ['.yaml','.yml']:yaml.safe_load(text)
 sizes.append(len(raw))
print(json.dumps({'files':len(paths),'json_python_yaml_syntax':'passed','newline_whitespace_conflict_private_key_checks':'passed','largest_native_file_bytes':max(sizes),'native_size_limit_bytes':150*1024},indent=2))
