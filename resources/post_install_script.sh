#!/bin/sh
echo "Begin remoteit-ssh post-install script..."

grep -R "remoteit-ssh" ~/.zshrc || echo '''
function _remoteit_ssh_wrapper() {
  output=$(_remoteit-ssh $1)

  if [[ "$output" == "ssh -o"* ]]; then
    eval $output
  else
    echo $output
  fi
}

alias remoteit-ssh="_remoteit_ssh_wrapper"
''' >> ~/.zshrc

echo "End remoteit-ssh post-install script."
