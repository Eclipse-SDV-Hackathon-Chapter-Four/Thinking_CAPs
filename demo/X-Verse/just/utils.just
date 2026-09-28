#!/usr/bin/env just --justfile

no_errors     := "-euo pipefail"
allow_errors  := "-uo pipefail"

wsl_user_perm := "0700"
wsl_user_dir  := "/run/user/1000/"

user_bashrc   := "~/.bashrc"

get_release   := `cat /etc/os-release | grep "^ID=" | cut -c4-`

hash_notice   := '''
#                                                                           \
#  Copyright (c) 2025 The X-Verse <https://github.com/The-Xverse>           \
#                                                                           \
#  Licensed under the Apache License, Version 2.0 (the "License");          \
#  you may not use this file except in compliance with the License.         \
#  You may obtain a copy of the License at                                  \
#                                                                           \
#      http://www.apache.org/licenses/LICENSE-2.0                           \
#                                                                           \
#  Unless required by applicable law or agreed to in writing, software      \
#  distributed under the License is distributed on an "AS IS" BASIS,        \
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. \
#  See the License for the specific language governing permissions and      \
#  limitations under the License.                                           \
#                                                                           \
'''

slash_notice  := '''
//                                                                          \
// Copyright (c) 2025 The X-Verse <https://github.com/The-Xverse>           \
//                                                                          \
// Licensed under the Apache License, Version 2.0 (the "License");          \
// you may not use this file except in compliance with the License.         \
// You may obtain a copy of the License at                                  \
//                                                                          \
//     http://www.apache.org/licenses/LICENSE-2.0                           \
//                                                                          \
// Unless required by applicable law or agreed to in writing, software      \
// distributed under the License is distributed on an "AS IS" BASIS,        \
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. \
// See the License for the specific language governing permissions and      \
// limitations under the License.                                           \
//                                                                          \
'''

# Verify that you are on the expected host
_check_host expected:
  #!/usr/bin/env -S bash
  set {{ no_errors }}
  actual={{ get_release }}
  if [[ -z "$actual" ]]; then
    just _halt_with_error "Unable to identify host!"
  elif [[ "$actual" != {{ expected }} ]]; then
    just _halt_with_error "The \'$actual\' host is different than \'{{ expected }}\'!"
  else
    echo -e "\nYou are running on host '$actual'."
  fi

# Clone a specific repository at a specific branch (regular clone)
_clone_repo repo branch directory:
  #!/usr/bin/env -S bash -x
  set {{ no_errors }}
  if ! [[ -d {{ directory }} ]]; then
    echo -e "\nCloning '{{ repo }}'..."
    echo -e "  Directory='{{ directory }}', Branch='{{ branch }}'"
    git clone \
      --branch {{ branch }} \
      --single-branch \
      {{ repo }} \
      {{ directory }}
  else
    just _halt_with_error "'{{ directory }}' already exists!"
  fi

# Clone a specific repository at a specific branch for sparse checkout
_clone_repo_sparse repo branch directory:
  #!/usr/bin/env -S bash -x
  set {{ no_errors }}
  if ! [[ -d {{ directory }} ]]; then
    echo -e "\nCloning (sparse) '{{ repo }}'..."
    echo -e "  Directory='{{ directory }}', Branch='{{ branch }}'"
    git clone \
      --no-checkout \
      --depth=1 \
      --filter=tree:0 \
      --branch {{ branch }} \
      --single-branch \
      {{ repo }} \
      {{ directory }}
  else
    just _halt_with_error "'{{ directory }}' already exists!"
  fi

# Download a file from a URL and verify the checksum
_download_file url file expected:
  #!/usr/bin/env -S bash -x
  set {{ no_errors }}
  if ! [[ -f {{ file }} ]]; then
    echo -e "\nDownloading '{{ file }}'..."
    wget {{ url }} -O {{ file }}
  else
    echo -e "\n'{{ file }}' is already downloaded!"
  fi
  if ! [[ -z {{ expected }} ]]; then
    echo -e "\nVerifying '{{ file }}'..."
    actual=`md5sum {{ file }} | awk '{print $1}'`
    if [[ "$actual" != {{ expected }} ]]; then
      just _halt_with_error "MD5 hashes do not match!"
    else
      echo -e "\nMD5 hash '$actual' matches!"
    fi
  fi

# Extract a .tgz file to a destination folder
_extract_file file directory:
  #!/usr/bin/env -S bash -x
  set {{ no_errors }}
  if [[ -f {{ file }} ]]; then
    if ! [[ -d {{ directory }} ]]; then
      mkdir {{ directory }}
      echo -e "\nExtracting '{{ file }}'..."
      tar -xzvf {{ file }} --directory {{ directory }}
    else
      just _halt_with_error "'{{ directory }}' already exists!"
    fi
  else
    just _halt_with_error "Could not find file '{{ file }}'!"
  fi

# Abort execution and report error message to user
_halt_with_error message:
  @echo {{ message }} && exit 1

# Insert a copyright notice (#) into a file at the first line
_insert_hash_notice file:
  #!/usr/bin/env -S bash -x
  set {{ no_errors }}
  if ! grep -iq "COPYRIGHT" "{{ file }}"; then
    echo -e "\nInserting copyright notice into '{{ file }}' at line '1'..."
    sed -i '1i{{ hash_notice }}' {{ file }}
    sed -i 's/[[:space:]]*$//' {{ file }}
  else
    echo -e "\nCopyright notice already exists in '{{ file }}'!"
  fi

# Insert a copyright notice (//) into a file at the first line
_insert_slash_notice file:
  #!/usr/bin/env -S bash -x
  set {{ no_errors }}
  if ! grep -iq "COPYRIGHT" "{{ file }}"; then
    echo -e "\nInserting copyright notice into '{{ file }}' at line '1'..."
    sed -i '1i{{ slash_notice }}' {{ file }}
    sed -i 's/[[:space:]]*$//' {{ file }}
  else
    echo -e "\nCopyright notice already exists in '{{ file }}'!"
  fi

# Show the information about a file
_list_file file:
  #!/usr/bin/env -S bash -x
  set {{ no_errors }}
  if [[ -f {{ file }} ]]; then
    ls -lah {{ file }}
  else
    just _halt_with_error "File '{{ file }}' does not exist!"
  fi

[group('Utilities')]
[doc('Check current host')]
check-host expected="ubuntu":
  @just _check_host {{ expected }}

[group('Utilities')]
[doc('Fix WSL permission issues')]
fix-wsl:
  @chmod {{ wsl_user_perm }} {{ wsl_user_dir }}
  @sed -i '/JUST/Id' {{ user_bashrc }}
  @echo "# Justfiles <https://github.com/casey/just>" >> {{ user_bashrc }}
  @echo "export JUST_TEMPDIR=\"/tmp\"" >> {{ user_bashrc }}
