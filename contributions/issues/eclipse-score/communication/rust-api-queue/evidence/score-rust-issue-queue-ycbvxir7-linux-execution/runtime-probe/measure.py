import json,subprocess
from pathlib import Path
ROOT=Path(__file__).parent
cwd=Path.cwd();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
(ROOT/'measured.json').write_text(json.dumps({'cwd':str(cwd),'resolved_cwd':str(cwd.resolve()),'head_before_command':head,'original_baseline':'381d43dec900ab6a9076f3f30e7bfbdee019e26e','baseline_unchanged':head=='381d43dec900ab6a9076f3f30e7bfbdee019e26e'})+'\n')
