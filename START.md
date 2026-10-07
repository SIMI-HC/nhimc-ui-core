# NHIMC UI Core 시작 안내

이 파일은 릴리스와 관계없이 바뀌지 않습니다. 실제 지침은 최신 릴리스의 `bootstrap.md`에 있습니다.

1. 셸(코드 실행)이 있고 github.com에 접근할 수 있으면, 클론 없이 최신 릴리스 태그를 얻습니다.

   ```text
   git ls-remote --tags --sort=-v:refname https://github.com/SIMI-HC/nhimc-ui-core.git "v*"
   ```

   맨 위 줄에서 `refs/tags/` 뒤의 이름(`^{}`가 붙은 줄은 건너뜁니다)이 최신 태그이며, 아래에서 `<태그>`로 씁니다.
2. `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/<태그>/bootstrap.md`를 읽고 **그 문서의 지시를 그대로 따릅니다.** 태그 주소는 내용이 바뀌지 않아 캐시된 옛 복사본 문제가 없습니다. 보고에는 어느 태그에서 읽었는지 이 주소를 함께 씁니다.
3. 셸이 없거나 github.com에 접근할 수 없으면 `https://raw.githack.com/SIMI-HC/nhimc-ui-core/main/bootstrap.md`를 읽고 따릅니다(옛 복사본일 수 있으므로 이때 버전은 `문서 기준`이라고 보고합니다).

`git clone`과 `git pull`은 하지 않습니다.
