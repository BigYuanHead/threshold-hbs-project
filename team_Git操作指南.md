# GitHub 团队开发与协作完整规范

本文件用于统一团队在 GitHub 上的开发、拉取、提交、推送、合并和冲突处理方式。  
目标是减少冲突、避免误覆盖、保证分支清晰，并让团队代码能够稳定整合。

---

# 1. 文档目的

本规范主要解决以下问题：

- 多人同时开发时分支混乱
- 没拉最新代码就开始写，导致后续冲突严重
- 直接把未完成代码 push 到共享分支
- 修改了公共接口但没有通知组员
- `main` 分支被频繁污染
- merge 冲突后乱删代码
- 强推覆盖别人代码

---

# 2. 总体原则

1. **不直接在 `main` 分支上开发**
2. **每个人只在自己的功能分支上开发**
3. **开发前先拉最新代码**
4. **推送前先测试**
5. **合并前先同步最新 `dev`**
6. **修改公共接口必须通知组员**
7. **不要随意使用 `git push --force`**
8. **共享分支必须保持基本可用**
9. **提交记录要清晰可追踪**
10. **出现冲突先理解逻辑，再处理**

---

# 3. 分支结构规范

建议统一使用以下分支结构：

- `main`：稳定版本，只放最终可运行、可展示、可交付的代码
- `dev`：团队整合分支，用于日常联调和模块整合
- `feature/...`：个人功能开发分支

---

# 4. 各分支职责

## 4.1 `main` 分支
`main` 只保留稳定版本，不做日常开发。

### 规则
- 不直接在 `main` 上写代码
- 不直接 push 日常开发内容到 `main`
- 只有在版本稳定后，才从 `dev` 合并到 `main`

### 错误例子

```bash
git checkout main
# 直接写代码
git add .
git commit -m "feat: add signing logic"
git push origin main
# GitHub 团队开发与协作完整规范

本文件用于统一团队在 GitHub 上的开发、拉取、提交、推送、合并和冲突处理方式。  
目标是减少冲突、避免误覆盖、保证分支清晰，并让团队代码能够稳定整合。

---

# 1. 文档目的

本规范主要解决以下问题：

- 多人同时开发时分支混乱
- 没拉最新代码就开始写，导致后续冲突严重
- 直接把未完成代码 push 到共享分支
- 修改了公共接口但没有通知组员
- `main` 分支被频繁污染
- merge 冲突后乱删代码
- 强推覆盖别人代码

---

# 2. 总体原则

1. **不直接在 `main` 分支上开发**
2. **每个人只在自己的功能分支上开发**
3. **开发前先拉最新代码**
4. **推送前先测试**
5. **合并前先同步最新 `dev`**
6. **修改公共接口必须通知组员**
7. **不要随意使用 `git push --force`**
8. **共享分支必须保持基本可用**
9. **提交记录要清晰可追踪**
10. **出现冲突先理解逻辑，再处理**

---

# 3. 分支结构规范

建议统一使用以下分支结构：

- `main`：稳定版本，只放最终可运行、可展示、可交付的代码
- `dev`：团队整合分支，用于日常联调和模块整合
- `feature/...`：个人功能开发分支

---

# 4. 各分支职责

## 4.1 `main` 分支
`main` 只保留稳定版本，不做日常开发。

### 规则
- 不直接在 `main` 上写代码
- 不直接 push 日常开发内容到 `main`
- 只有在版本稳定后，才从 `dev` 合并到 `main`

### 错误例子

```bash
git checkout main
# 直接写代码
git add .
git commit -m "feat: add signing logic"
git push origin main
```

### 正确例子

```bash
git checkout dev
git pull origin dev
git checkout -b feature/distributed-signing
```

---

## 4.2 `dev` 分支
`dev` 是团队整合分支，用于：

- 各模块合并
- 联调
- 集成测试
- 准备最终进入 `main`

### 规则
- 每个人完成自己的功能后，先合并到 `dev`
- `dev` 应保持基本可运行
- 不要把明显跑不通的代码合并进 `dev`

### 例子

你完成了 benchmark 模块后：

```bash
git checkout dev
git pull origin dev
git merge feature/benchmark
git push origin dev
```

---

## 4.3 `feature/...` 分支
每位成员主要在自己的功能分支上开发。

### 推荐命名
- `feature/lamport-core`
- `feature/additive-shares`
- `feature/distributed-signing`
- `feature/verification`
- `feature/benchmark`

### 规则
- 功能分支从最新 `dev` 创建
- 每个人主要维护自己的功能分支
- 未完成功能不要直接进入 `main`

### 例子

如果你负责 verification：

```bash
git checkout dev
git pull origin dev
git checkout -b feature/verification
```

---

# 5. 开发前操作规范

每次开始开发前，必须先同步远程最新代码。

## 标准流程

```bash
git checkout dev
git pull origin dev
```

如果自己的功能分支已经存在，再切回去并同步最新 `dev`：

```bash
git checkout feature/verification
git merge dev
```

---

## 为什么要这样做

如果你不先同步最新 `dev`，可能会出现：

- 基于旧代码开发
- 后续 merge 冲突严重
- 本地测试通过，但和团队代码合不起来
- 覆盖别人新加的内容

---

## 完整例子

你今天开始继续写 verification：

```bash
git checkout dev
git pull origin dev
git checkout feature/verification
git merge dev
```

这样你就基于团队最新代码继续开发。

---

# 6. 新建功能分支规范

如果你还没有自己的功能分支，必须从最新的 `dev` 创建。

## 正确做法

```bash
git checkout dev
git pull origin dev
git checkout -b feature/lamport-core
```

## 不推荐做法

```bash
git checkout some-old-branch
git checkout -b feature/lamport-core
```

因为这可能把旧版本代码和历史错误一起带过去。

---

# 7. 日常开发与提交规范

## 7.1 小步提交
每次 commit 只处理一个明确改动，不要把很多无关修改混在一起。

### 好的例子

```bash
git add core/lamport.py
git commit -m "feat: implement Lamport key generation"

git add tests/test_lamport.py
git commit -m "test: add Lamport sign and verify test"
```

### 不好的例子

```bash
git add .
git commit -m "update"
```

```bash
git add .
git commit -m "final final version"
```

这种写法看不出你到底改了什么。

---

## 7.2 commit message 规范

建议格式：

```text
type: 简短描述
```

### 常用类型
- `feat`：新增功能
- `fix`：修复 bug
- `test`：测试相关
- `docs`：文档修改
- `refactor`：代码重构

### 推荐例子

```bash
git commit -m "feat: implement distributed signing workflow"
git commit -m "fix: correct signature verification logic"
git commit -m "test: add end-to-end signing test"
git commit -m "docs: update setup instructions"
```

---

# 8. 推送前检查规范

在 push 之前，必须先确认代码处于可提交状态。

## push 前检查清单

- 代码可以运行
- 相关测试通过
- 没有明显 debug 输出
- 没有无用文件
- 如果改了接口，文档已更新
- 如果改了公共逻辑，组员已知情

---

## 例子

推送前先执行：

```bash
python main.py
pytest
```

确认没有报错后再 push：

```bash
git push origin feature/verification
```

---

# 9. 推送规范

## 9.1 第一次推送功能分支

```bash
git push -u origin feature/verification
```

## 9.2 之后继续推送

```bash
git push origin feature/verification
```

---

## 9.3 推送前必须同步最新 `dev`

为了尽量减少冲突，推送前建议先更新 `dev` 并合并到自己的功能分支。

### 标准流程

```bash
git checkout dev
git pull origin dev
git checkout feature/verification
git merge dev
```

如果没有问题，再测试并推送：

```bash
pytest
git push origin feature/verification
```

---

## 为什么这样做

假设你今天改了 `verification.py`，而别人改了 `party.py` 和 `signing.py`。  
如果你不先 merge 最新 `dev`，就直接 push，后面统一合并时更容易出问题。

---

# 10. 合并规范

## 10.1 功能分支先合并到 `dev`
每个模块完成后，应先进入 `dev`，而不是直接进 `main`。

### 正确流程
1. 在自己的 `feature/...` 分支完成开发
2. 同步最新 `dev`
3. 解决冲突
4. 跑测试
5. 合并到 `dev`

### 例子

```bash
git checkout dev
git pull origin dev
git merge feature/additive-shares
git push origin dev
```

---

## 10.2 `dev` 再合并到 `main`
只有在下面条件满足时，才允许从 `dev` 合并到 `main`：

- 主流程可以跑通
- 关键测试通过
- demo 可展示
- README 与代码一致
- 当前版本适合对外展示或提交

### 例子

可以 merge 到 `main` 的情况：
- `main.py` 能跑完整流程
- `pytest` 通过
- benchmark 脚本能运行
- README 写清楚了运行方式

不可以 merge 到 `main` 的情况：
- verification 还有已知 bug
- benchmark 结果没检查
- 文档和代码接口不一致

---

# 11. Pull Request 规范

如果条件允许，建议所有功能分支通过 Pull Request 合并到 `dev`。

## 推荐流程
1. 在本地完成功能
2. push 到远程功能分支
3. 在 GitHub 上发起 PR
4. 让至少一位组员简单检查
5. 确认后合并到 `dev`

---

## 例子

你完成 `feature/additive-shares` 后：

```bash
git push origin feature/additive-shares
```

然后在 GitHub 上发起：

- base: `dev`
- compare: `feature/additive-shares`

检查内容包括：

- 命名是否清晰
- 是否影响公共接口
- 测试是否通过
- 是否引入明显 bug

---

## 好处

- 更容易发现问题
- 更容易追踪改动
- 更方便沟通
- 更不容易把错误直接合进共享分支

---

# 12. 公共接口修改规范

如果你修改了别人会调用的函数、类、参数或返回值，必须通知组员，并同步更新文档。

---

## 例子

原本函数是：

```python
def verify_signature(message, signature, public_key):
    ...
```

你改成：

```python
def verify_signature(message, signature, public_key, auth_path):
    ...
```

那么你不能只 push 代码就结束。  
你还必须：

- 告诉组员函数增加了 `auth_path`
- 提醒调用这个函数的模块同步修改
- 更新 README 或接口说明

---

## 为什么必须这样做

否则别的组员拉代码后会出现：

- 参数数量不匹配
- 调用报错
- 本地代码突然跑不通
- 找不到问题来源

---

# 13. 冲突处理规范

merge 或 pull 时出现冲突，不要乱删代码。

---

## 标准处理流程

1. 看清楚哪个文件冲突
2. 理解双方修改内容
3. 判断应该保留哪部分，或手动合并
4. 冲突解决后重新测试
5. 再 commit

---

## 例子

执行：

```bash
git merge dev
```

出现：

```text
CONFLICT (content): Merge conflict in protocol/signing.py
```

处理步骤：

1. 打开 `protocol/signing.py`
2. 找到冲突标记
3. 理解双方逻辑
4. 手动合并
5. 保存后执行：

```bash
git add protocol/signing.py
git commit -m "fix: resolve merge conflict in signing workflow"
```

---

## 不推荐做法

- 看到冲突就全部删掉
- 不理解代码就只保留自己的版本
- 不测试就继续 push

---

# 14. 强推规范

除非组内明确同意，否则不要使用：

```bash
git push --force
```

---

## 为什么危险

强推会改写远程历史，可能直接覆盖别人已经提交的代码。

---

## 危险例子

```bash
git push --force origin dev
```

这可能把组员已经合并进 `dev` 的内容全部顶掉。

---

## 只有在什么情况下才可能使用

- 只操作自己的个人分支
- 没有其他人依赖该分支
- 组内知道你在重写历史
- 你确认不会覆盖别人工作

即使如此，也应非常谨慎。

---

# 15. 无用文件清理规范

push 前必须检查当前工作区，避免把垃圾文件提交上去。

---

## 不应提交的内容

- 临时测试文件
- 本地 debug 日志
- 截图
- IDE 缓存文件
- 系统自动生成文件
- 无意义备份文件

---

## 常见例子

不建议提交：

- `test2_final_final.py`
- `debug_output.txt`
- `.DS_Store`
- `.idea/`
- `__pycache__/`

---

## 建议操作

先看状态：

```bash
git status
```

如果出现不该提交的文件，先删除或加入 `.gitignore`。

---

# 16. 每日推荐工作流

下面是推荐的日常开发流程。

---

## 16.1 开始开发前

```bash
git checkout dev
git pull origin dev
git checkout feature/your-branch
git merge dev
```

---

## 16.2 开发过程中

```bash
git add .
git commit -m "feat: your update"
```

---

## 16.3 推送前

```bash
python main.py
pytest
git push origin feature/your-branch
```

---

## 16.4 准备合并前

- 再同步一次最新 `dev`
- 解决冲突
- 再跑一次测试
- 再发 PR 或 merge

---

# 17. 一个完整开发例子

下面给出一个从开始开发到推送的完整示例。

假设你负责 `verification` 模块。

---

## Step 1：同步最新代码

```bash
git checkout dev
git pull origin dev
```

---

## Step 2：切换到自己的功能分支

如果分支还没有，就新建：

```bash
git checkout -b feature/verification
```

如果已经有：

```bash
git checkout feature/verification
git merge dev
```

---

## Step 3：开始开发并提交

```bash
git add entities/verifier.py
git commit -m "feat: implement final signature verification"
```

如果你还补了测试：

```bash
git add tests/test_verification.py
git commit -m "test: add verification unit tests"
```

---

## Step 4：推送前同步最新 `dev`

```bash
git checkout dev
git pull origin dev
git checkout feature/verification
git merge dev
```

---

## Step 5：运行测试

```bash
python main.py
pytest
```

---

## Step 6：推送到远程

第一次：

```bash
git push -u origin feature/verification
```

之后：

```bash
git push origin feature/verification
```

---

## Step 7：发起 PR 或请求合并

在 GitHub 上发起：

- base: `dev`
- compare: `feature/verification`

然后请组员看一眼再合并。

---

# 18. 最简执行版规则

如果只记最核心内容，请至少遵守这几条：

1. 开发前先 `pull`
2. 只在自己的 `feature` 分支开发
3. push 前先测试
4. 不直接改 `main`
5. merge 前先同步最新 `dev`
6. 不随便 `force push`
7. 改公共接口一定通知组员

---

## 最简例子

```bash
git checkout dev
git pull origin dev
git checkout -b feature/verification

# 开发
git add .
git commit -m "feat: implement final signature verification"

# 同步 dev
git checkout dev
git pull origin dev
git checkout feature/verification
git merge dev

# 测试并推送
pytest
git push origin feature/verification
```

---

# 19. 最终要求

团队协作不是“把代码推上去就行”，而是要保证：

- 不影响别人开发
- 不覆盖别人代码
- 共享分支尽量稳定
- 改动记录清楚
- 最终项目能顺利整合、测试和展示

因此每次：

- 拉取
- 开发
- 提交
- 推送
- 合并
- 处理冲突

都应按照本规范执行。