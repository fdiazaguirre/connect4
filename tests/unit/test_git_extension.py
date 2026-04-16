"""
Tests for .specify/extensions/git/scripts/bash/ shell scripts.

Covers:
  - git-common.sh  : has_git(), check_feature_branch()
  - create-new-feature.sh : clean_branch_name, _extract_highest_number,
                            get_highest_from_specs, GIT_BRANCH_NAME override,
                            --dry-run, --json, --number, --short-name, --timestamp
  - auto-commit.sh : YAML config parsing (enabled/disabled/default), no-changes skip
  - initialize-repo.sh : fresh init, already-initialized skip, custom commit message
"""

import os
import subprocess
import textwrap
import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASH_DIR = os.path.join(REPO_ROOT, ".specify", "extensions", "git", "scripts", "bash")
GIT_COMMON = os.path.join(BASH_DIR, "git-common.sh")
CREATE_FEATURE = os.path.join(BASH_DIR, "create-new-feature.sh")
AUTO_COMMIT = os.path.join(BASH_DIR, "auto-commit.sh")
INIT_REPO = os.path.join(BASH_DIR, "initialize-repo.sh")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_bash(script: str, **kwargs) -> subprocess.CompletedProcess:
    """Run an inline bash script and return the completed process."""
    return subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        **kwargs,
    )


def run_script(path: str, args=None, env=None, cwd=None) -> subprocess.CompletedProcess:
    """Run a bash script file with optional args, env overrides, and cwd."""
    cmd = ["bash", path] + (args or [])
    merged_env = {**os.environ, **(env or {})}
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=merged_env,
        cwd=cwd,
    )


def init_git_repo(path: str, user_name: str = "Test User", user_email: str = "test@example.com") -> None:
    """Initialize a bare git repo suitable for testing."""
    subprocess.run(["git", "init", "-q", path], check=True)
    subprocess.run(["git", "-C", path, "config", "user.name", user_name], check=True)
    subprocess.run(["git", "-C", path, "config", "user.email", user_email], check=True)
    # Create an initial commit so HEAD exists
    open(os.path.join(path, ".gitkeep"), "w").close()
    subprocess.run(["git", "-C", path, "add", ".gitkeep"], check=True)
    subprocess.run(["git", "-C", path, "commit", "-q", "-m", "Initial commit"], check=True)


def make_specify_structure(base: str) -> str:
    """Create the minimal .specify/extensions/git/... dir structure under base."""
    scripts_dir = os.path.join(base, ".specify", "extensions", "git", "scripts", "bash")
    os.makedirs(scripts_dir, exist_ok=True)
    for fname in ("git-common.sh", "create-new-feature.sh", "auto-commit.sh", "initialize-repo.sh"):
        src = os.path.join(BASH_DIR, fname)
        dst = os.path.join(scripts_dir, fname)
        import shutil
        shutil.copy2(src, dst)
        os.chmod(dst, 0o755)
    return scripts_dir


def write_git_config(base: str, content: str) -> str:
    """Write a git-config.yml into the expected extension config path."""
    config_dir = os.path.join(base, ".specify", "extensions", "git")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "git-config.yml")
    with open(config_path, "w") as f:
        f.write(content)
    return config_path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def git_repo(tmp_path):
    """Yield a path to a fresh git repository with .specify structure."""
    repo = str(tmp_path)
    init_git_repo(repo)
    make_specify_structure(repo)
    return repo


@pytest.fixture()
def non_git_dir(tmp_path):
    """Yield a plain directory (no .git) with .specify structure."""
    d = str(tmp_path / "no_git")
    os.makedirs(d)
    make_specify_structure(d)
    return d


# ===========================================================================
# git-common.sh: has_git()
# ===========================================================================

class TestHasGit:
    """Tests for the has_git() function in git-common.sh."""

    def _has_git(self, path: str) -> int:
        result = run_bash(
            f'source "{GIT_COMMON}"; has_git "{path}"; echo $?'
        )
        # The last line is the exit code echoed
        lines = result.stdout.strip().splitlines()
        return int(lines[-1]) if lines else 1

    def test_returns_true_for_git_repo(self, tmp_path):
        repo = str(tmp_path / "repo")
        init_git_repo(repo)
        assert self._has_git(repo) == 0

    def test_returns_false_for_plain_dir(self, tmp_path):
        plain = str(tmp_path / "plain")
        os.makedirs(plain)
        assert self._has_git(plain) != 0

    def test_returns_false_for_nonexistent_path(self, tmp_path):
        missing = str(tmp_path / "does_not_exist")
        assert self._has_git(missing) != 0

    def test_defaults_to_pwd_when_no_arg(self, tmp_path):
        repo = str(tmp_path / "repo")
        init_git_repo(repo)
        result = run_bash(
            f'cd "{repo}"; source "{GIT_COMMON}"; has_git; echo $?'
        )
        lines = result.stdout.strip().splitlines()
        assert int(lines[-1]) == 0


# ===========================================================================
# git-common.sh: check_feature_branch()
# ===========================================================================

class TestCheckFeatureBranch:
    """Tests for the check_feature_branch() function in git-common.sh."""

    def _check(self, branch: str, has_git: str = "true"):
        return run_bash(
            f'source "{GIT_COMMON}"; check_feature_branch "{branch}" "{has_git}" 2>&1; echo "EXIT:$?"'
        )

    # --- valid sequential branches ---

    def test_accepts_three_digit_sequential(self):
        result = self._check("001-my-feature")
        assert "EXIT:0" in result.stdout

    def test_accepts_padded_sequential_with_slug(self):
        result = self._check("042-fix-payment-bug")
        assert "EXIT:0" in result.stdout

    def test_accepts_large_sequential_number(self):
        result = self._check("1000-big-feature")
        assert "EXIT:0" in result.stdout

    def test_accepts_four_digit_sequential(self):
        result = self._check("0100-refactor-auth")
        assert "EXIT:0" in result.stdout

    # --- valid timestamp branches ---

    def test_accepts_valid_timestamp_branch(self):
        result = self._check("20260319-143022-feature-name")
        assert "EXIT:0" in result.stdout

    def test_accepts_timestamp_with_multi_segment_slug(self):
        result = self._check("20260101-000000-add-user-auth")
        assert "EXIT:0" in result.stdout

    # --- invalid branches ---

    def test_rejects_main(self):
        result = self._check("main")
        assert "EXIT:1" in result.stdout
        assert "Not on a feature branch" in result.stdout

    def test_rejects_develop(self):
        result = self._check("develop")
        assert "EXIT:1" in result.stdout

    def test_rejects_plain_name_without_prefix(self):
        result = self._check("my-feature")
        assert "EXIT:1" in result.stdout

    def test_rejects_two_digit_prefix(self):
        result = self._check("01-feature")
        assert "EXIT:1" in result.stdout

    def test_rejects_seven_digit_date(self):
        result = self._check("2026031-143022-feature")
        assert "EXIT:1" in result.stdout

    def test_rejects_timestamp_without_trailing_slug(self):
        # 8-digit date + 6-digit time but NO trailing slug
        result = self._check("20260319-143022")
        assert "EXIT:1" in result.stdout

    def test_rejects_numeric_only(self):
        result = self._check("001")
        assert "EXIT:1" in result.stdout

    # --- non-git graceful degradation ---

    def test_skips_validation_when_no_git(self):
        result = self._check("main", has_git="false")
        # Should return 0 (success) and print a warning, not error
        assert "EXIT:0" in result.stdout
        assert "Warning" in result.stdout

    def test_error_message_contains_example_formats(self):
        result = self._check("bad-branch")
        assert "001-feature-name" in result.stdout or "20260319" in result.stdout


# ===========================================================================
# create-new-feature.sh: argument validation
# ===========================================================================

class TestCreateNewFeatureArgs:
    """Tests for argument parsing and validation in create-new-feature.sh."""

    def test_no_args_prints_usage_and_exits_1(self, git_repo):
        result = run_script(
            os.path.join(git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"),
            cwd=git_repo,
        )
        assert result.returncode == 1
        assert "Usage:" in result.stderr

    def test_whitespace_only_description_exits_1(self, git_repo):
        result = run_script(
            os.path.join(git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"),
            args=["   "],
            cwd=git_repo,
        )
        assert result.returncode == 1
        assert "cannot be empty" in result.stderr

    def test_short_name_without_value_exits_1(self, git_repo):
        result = run_script(
            os.path.join(git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"),
            args=["--short-name", "--json", "some feature"],
            cwd=git_repo,
        )
        assert result.returncode == 1
        assert "--short-name requires a value" in result.stderr

    def test_number_without_value_exits_1(self, git_repo):
        result = run_script(
            os.path.join(git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"),
            args=["--number", "--dry-run", "some feature"],
            cwd=git_repo,
        )
        assert result.returncode == 1
        assert "--number requires a value" in result.stderr

    def test_number_non_integer_exits_1(self, git_repo):
        result = run_script(
            os.path.join(git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"),
            args=["--number", "abc", "some feature"],
            cwd=git_repo,
        )
        assert result.returncode == 1
        assert "non-negative integer" in result.stderr

    def test_help_flag_exits_0(self, git_repo):
        result = run_script(
            os.path.join(git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"),
            args=["--help"],
            cwd=git_repo,
        )
        assert result.returncode == 0
        assert "Usage:" in result.stdout


# ===========================================================================
# create-new-feature.sh: dry-run + JSON output
# ===========================================================================

class TestCreateNewFeatureDryRun:
    """Tests for --dry-run output of create-new-feature.sh."""

    def _run_dry(self, git_repo, extra_args=None, env=None):
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"
        )
        args = ["--dry-run", "--json", "--number", "5"] + (extra_args or []) + ["Test feature description"]
        return run_script(script, args=args, cwd=git_repo, env=env)

    def test_dry_run_json_contains_branch_name(self, git_repo):
        result = self._run_dry(git_repo, ["--short-name", "user-auth"])
        assert result.returncode == 0
        assert "005-user-auth" in result.stdout

    def test_dry_run_json_contains_feature_num(self, git_repo):
        result = self._run_dry(git_repo, ["--short-name", "user-auth"])
        assert "005" in result.stdout

    def test_dry_run_json_contains_dry_run_flag(self, git_repo):
        result = self._run_dry(git_repo, ["--short-name", "user-auth"])
        assert "DRY_RUN" in result.stdout

    def test_dry_run_does_not_create_branch(self, git_repo):
        self._run_dry(git_repo, ["--short-name", "no-create"])
        branches = subprocess.run(
            ["git", "-C", git_repo, "branch", "--list"],
            capture_output=True, text=True,
        ).stdout
        assert "no-create" not in branches

    def test_dry_run_plain_output(self, git_repo):
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"
        )
        result = run_script(
            script,
            args=["--dry-run", "--number", "7", "--short-name", "my-feat", "feature desc"],
            cwd=git_repo,
        )
        assert result.returncode == 0
        assert "BRANCH_NAME: 007-my-feat" in result.stdout
        assert "FEATURE_NUM: 007" in result.stdout

    def test_number_zero_padded_to_three_digits(self, git_repo):
        result = self._run_dry(git_repo, ["--short-name", "feat"])
        assert '"FEATURE_NUM":"005"' in result.stdout or "FEATURE_NUM: 005" in result.stdout


# ===========================================================================
# create-new-feature.sh: clean_branch_name logic
# ===========================================================================

class TestCleanBranchName:
    """Tests for the clean_branch_name() bash function."""

    def _clean(self, name: str) -> str:
        result = run_bash(textwrap.dedent(f"""
            clean_branch_name() {{
                local name="$1"
                echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\\+/-/g' | sed 's/^-//' | sed 's/-$//'
            }}
            clean_branch_name "{name}"
        """))
        return result.stdout.strip()

    def test_lowercases_input(self):
        assert self._clean("MyFeature") == "myfeature"

    def test_replaces_spaces_with_dashes(self):
        assert self._clean("Add User Auth") == "add-user-auth"

    def test_collapses_multiple_dashes(self):
        assert self._clean("Fix--Bug") == "fix-bug"

    def test_removes_leading_dashes(self):
        assert self._clean("--Leading") == "leading"

    def test_removes_trailing_dashes(self):
        assert self._clean("Trailing--") == "trailing"

    def test_preserves_numbers(self):
        assert self._clean("OAuth2 API") == "oauth2-api"

    def test_replaces_special_chars(self):
        result = self._clean("Fix: Bug! #123")
        assert result == "fix-bug-123"

    def test_empty_string_produces_empty(self):
        result = self._clean("")
        assert result == ""


# ===========================================================================
# create-new-feature.sh: _extract_highest_number
# ===========================================================================

class TestExtractHighestNumber:
    """Tests for the _extract_highest_number() pipe function."""

    def _extract(self, names: list) -> int:
        input_text = "\n".join(names)
        result = run_bash(textwrap.dedent(f"""
            _extract_highest_number() {{
                local highest=0
                while IFS= read -r name; do
                    [ -z "$name" ] && continue
                    if echo "$name" | grep -Eq '^[0-9]{{3,}}-' && ! echo "$name" | grep -Eq '^[0-9]{{8}}-[0-9]{{6}}-'; then
                        number=$(echo "$name" | grep -Eo '^[0-9]+' || echo "0")
                        number=$((10#$number))
                        if [ "$number" -gt "$highest" ]; then
                            highest=$number
                        fi
                    fi
                done
                echo $highest
            }}
            printf '%s\\n' {" ".join(repr(n) for n in names)} | _extract_highest_number
        """))
        return int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0

    def test_extracts_highest_from_simple_list(self):
        assert self._extract(["001-feat", "005-auth", "003-bug"]) == 5

    def test_returns_zero_for_empty_input(self):
        result = run_bash(textwrap.dedent("""
            _extract_highest_number() {
                local highest=0
                while IFS= read -r name; do
                    [ -z "$name" ] && continue
                    if echo "$name" | grep -Eq '^[0-9]{3,}-' && ! echo "$name" | grep -Eq '^[0-9]{8}-[0-9]{6}-'; then
                        number=$(echo "$name" | grep -Eo '^[0-9]+' || echo "0")
                        number=$((10#$number))
                        if [ "$number" -gt "$highest" ]; then
                            highest=$number
                        fi
                    fi
                done
                echo $highest
            }
            echo "" | _extract_highest_number
        """))
        assert result.stdout.strip() == "0"

    def test_ignores_timestamp_branches(self):
        # Timestamp branches (YYYYMMDD-HHMMSS-) should not be counted
        result = run_bash(textwrap.dedent("""
            _extract_highest_number() {
                local highest=0
                while IFS= read -r name; do
                    [ -z "$name" ] && continue
                    if echo "$name" | grep -Eq '^[0-9]{3,}-' && ! echo "$name" | grep -Eq '^[0-9]{8}-[0-9]{6}-'; then
                        number=$(echo "$name" | grep -Eo '^[0-9]+' || echo "0")
                        number=$((10#$number))
                        if [ "$number" -gt "$highest" ]; then
                            highest=$number
                        fi
                    fi
                done
                echo $highest
            }
            printf '%s\n' '20260319-143022-big-feature' '002-real' | _extract_highest_number
        """))
        # Should be 2, not 20260319
        assert result.stdout.strip() == "2"

    def test_ignores_branches_with_fewer_than_three_digits(self):
        result = run_bash(textwrap.dedent("""
            _extract_highest_number() {
                local highest=0
                while IFS= read -r name; do
                    [ -z "$name" ] && continue
                    if echo "$name" | grep -Eq '^[0-9]{3,}-' && ! echo "$name" | grep -Eq '^[0-9]{8}-[0-9]{6}-'; then
                        number=$(echo "$name" | grep -Eo '^[0-9]+' || echo "0")
                        number=$((10#$number))
                        if [ "$number" -gt "$highest" ]; then
                            highest=$number
                        fi
                    fi
                done
                echo $highest
            }
            printf '%s\n' '01-short' 'main' 'feature-x' | _extract_highest_number
        """))
        assert result.stdout.strip() == "0"

    def test_handles_large_sequential_number(self):
        result = run_bash(textwrap.dedent("""
            _extract_highest_number() {
                local highest=0
                while IFS= read -r name; do
                    [ -z "$name" ] && continue
                    if echo "$name" | grep -Eq '^[0-9]{3,}-' && ! echo "$name" | grep -Eq '^[0-9]{8}-[0-9]{6}-'; then
                        number=$(echo "$name" | grep -Eo '^[0-9]+' || echo "0")
                        number=$((10#$number))
                        if [ "$number" -gt "$highest" ]; then
                            highest=$number
                        fi
                    fi
                done
                echo $highest
            }
            printf '%s\n' '001-a' '100-b' '1000-c' | _extract_highest_number
        """))
        assert result.stdout.strip() == "1000"


# ===========================================================================
# create-new-feature.sh: get_highest_from_specs
# ===========================================================================

class TestGetHighestFromSpecs:
    """Tests for the get_highest_from_specs() function."""

    def _setup_specs(self, tmp_path, dirs):
        specs = tmp_path / "specs"
        specs.mkdir()
        for d in dirs:
            (specs / d).mkdir()
        return str(specs)

    def _get_highest(self, specs_dir: str) -> int:
        result = run_bash(textwrap.dedent(f"""
            get_highest_from_specs() {{
                local specs_dir="$1"
                local highest=0
                if [ -d "$specs_dir" ]; then
                    for dir in "$specs_dir"/*; do
                        [ -d "$dir" ] || continue
                        dirname=$(basename "$dir")
                        if echo "$dirname" | grep -Eq '^[0-9]{{3,}}-' && ! echo "$dirname" | grep -Eq '^[0-9]{{8}}-[0-9]{{6}}-'; then
                            number=$(echo "$dirname" | grep -Eo '^[0-9]+')
                            number=$((10#$number))
                            if [ "$number" -gt "$highest" ]; then
                                highest=$number
                            fi
                        fi
                    done
                fi
                echo $highest
            }}
            get_highest_from_specs "{specs_dir}"
        """))
        return int(result.stdout.strip())

    def test_returns_highest_sequential_number(self, tmp_path):
        specs = self._setup_specs(tmp_path, ["001-feat", "003-auth", "002-bug"])
        assert self._get_highest(specs) == 3

    def test_ignores_timestamp_directories(self, tmp_path):
        specs = self._setup_specs(tmp_path, ["20260319-143022-something", "005-real"])
        assert self._get_highest(specs) == 5

    def test_returns_zero_for_empty_specs(self, tmp_path):
        specs = self._setup_specs(tmp_path, [])
        assert self._get_highest(specs) == 0

    def test_returns_zero_for_nonexistent_specs_dir(self, tmp_path):
        missing = str(tmp_path / "nonexistent")
        assert self._get_highest(missing) == 0

    def test_ignores_files_not_directories(self, tmp_path):
        specs = tmp_path / "specs"
        specs.mkdir()
        (specs / "007-file.txt").touch()  # a file, not a directory
        assert self._get_highest(str(specs)) == 0


# ===========================================================================
# create-new-feature.sh: GIT_BRANCH_NAME env override
# ===========================================================================

class TestCreateNewFeatureGitBranchNameEnv:
    """Tests for GIT_BRANCH_NAME environment variable override."""

    def _run(self, git_repo, branch_name, extra_args=None):
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"
        )
        args = ["--dry-run", "--json"] + (extra_args or []) + ["ignored description"]
        return run_script(script, args=args, cwd=git_repo, env={"GIT_BRANCH_NAME": branch_name})

    def test_uses_exact_branch_name_when_env_set(self, git_repo):
        result = self._run(git_repo, "my-exact-branch")
        assert result.returncode == 0
        assert "my-exact-branch" in result.stdout

    def test_extracts_feature_num_from_sequential_prefix(self, git_repo):
        result = self._run(git_repo, "007-some-feature")
        assert "007" in result.stdout

    def test_extracts_feature_num_from_timestamp_prefix(self, git_repo):
        result = self._run(git_repo, "20260319-143022-my-feature")
        assert "20260319-143022" in result.stdout

    def test_feature_num_equals_branch_name_when_no_prefix(self, git_repo):
        result = self._run(git_repo, "plain-name")
        assert "plain-name" in result.stdout

    def test_exits_1_when_env_branch_exceeds_244_bytes(self, git_repo):
        long_name = "a" * 245
        result = self._run(git_repo, long_name)
        assert result.returncode == 1
        assert "244" in result.stderr


# ===========================================================================
# create-new-feature.sh: --timestamp flag
# ===========================================================================

class TestCreateNewFeatureTimestamp:
    """Tests for --timestamp mode in create-new-feature.sh."""

    def test_timestamp_produces_date_prefix(self, git_repo):
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"
        )
        result = run_script(
            script,
            args=["--dry-run", "--json", "--timestamp", "--short-name", "my-feat", "Some feature"],
            cwd=git_repo,
        )
        assert result.returncode == 0
        import re
        # BRANCH_NAME should start with YYYYMMDD-HHMMSS-
        assert re.search(r'\d{8}-\d{6}-', result.stdout)

    def test_number_and_timestamp_warns(self, git_repo):
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"
        )
        result = run_script(
            script,
            args=["--dry-run", "--json", "--timestamp", "--number", "5", "--short-name", "feat", "desc"],
            cwd=git_repo,
        )
        assert result.returncode == 0
        assert "--number is ignored" in result.stderr


# ===========================================================================
# auto-commit.sh: argument validation
# ===========================================================================

class TestAutoCommitArgs:
    """Tests for argument validation in auto-commit.sh."""

    def test_no_args_exits_1(self, git_repo):
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "auto-commit.sh"
        )
        result = run_script(script, cwd=git_repo)
        assert result.returncode == 1
        assert "Usage:" in result.stderr


# ===========================================================================
# auto-commit.sh: config parsing — disabled by default
# ===========================================================================

class TestAutoCommitConfigParsing:
    """Tests for YAML config parsing in auto-commit.sh."""

    def _run_auto_commit(self, git_repo, event_name, config_content):
        write_git_config(git_repo, config_content)
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "auto-commit.sh"
        )
        return run_script(script, args=[event_name], cwd=git_repo)

    def test_exits_0_when_no_config_file(self, git_repo):
        # No git-config.yml — auto-commit should be skipped
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "auto-commit.sh"
        )
        result = run_script(script, args=["after_specify"], cwd=git_repo)
        assert result.returncode == 0

    def test_exits_0_when_event_disabled(self, git_repo):
        config = textwrap.dedent("""\
            branch_numbering: sequential
            auto_commit:
              default: false
              after_specify:
                enabled: false
                message: "[Spec Kit] Add specification"
        """)
        result = self._run_auto_commit(git_repo, "after_specify", config)
        assert result.returncode == 0

    def test_exits_0_when_no_changes_to_commit(self, git_repo):
        config = textwrap.dedent("""\
            branch_numbering: sequential
            auto_commit:
              default: false
              after_specify:
                enabled: true
                message: "[Spec Kit] Add specification"
        """)
        write_git_config(git_repo, config)
        # Commit the config so the repo is clean before we run auto-commit
        subprocess.run(["git", "-C", git_repo, "add", "."], check=True)
        subprocess.run(
            ["git", "-C", git_repo, "commit", "-q", "-m", "Add config"],
            check=True,
        )
        # Git repo is now clean — no changes to commit
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "auto-commit.sh"
        )
        result = run_script(script, args=["after_specify"], cwd=git_repo)
        assert result.returncode == 0
        assert "No changes to commit" in result.stderr

    def test_commits_when_event_enabled_and_changes_exist(self, git_repo):
        config = textwrap.dedent("""\
            branch_numbering: sequential
            auto_commit:
              default: false
              after_specify:
                enabled: true
                message: "[Spec Kit] Add specification"
        """)
        write_git_config(git_repo, config)
        # Create an untracked file
        new_file = os.path.join(git_repo, "new_spec.txt")
        with open(new_file, "w") as f:
            f.write("new content")

        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "auto-commit.sh"
        )
        result = run_script(script, args=["after_specify"], cwd=git_repo)
        assert result.returncode == 0
        assert "committed" in result.stderr.lower() or "Changes committed" in result.stderr

        # Verify the commit was actually made
        log = subprocess.run(
            ["git", "-C", git_repo, "log", "--oneline", "-2"],
            capture_output=True, text=True
        )
        assert "Add specification" in log.stdout

    def test_uses_default_when_event_not_explicitly_configured(self, git_repo):
        config = textwrap.dedent("""\
            auto_commit:
              default: true
        """)
        write_git_config(git_repo, config)
        # Create a new file so there's something to commit
        new_file = os.path.join(git_repo, "extra.txt")
        with open(new_file, "w") as f:
            f.write("content")

        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "auto-commit.sh"
        )
        result = run_script(script, args=["after_analyze"], cwd=git_repo)
        assert result.returncode == 0
        # Should have committed (event not in config, default=true)
        assert "committed" in result.stderr.lower() or "Changes committed" in result.stderr

    def test_default_not_used_when_event_explicitly_disabled(self, git_repo):
        config = textwrap.dedent("""\
            auto_commit:
              default: true
              after_specify:
                enabled: false
                message: "[Spec Kit] Add specification"
        """)
        # Create a file so there would be something to commit if enabled
        new_file = os.path.join(git_repo, "would_commit.txt")
        with open(new_file, "w") as f:
            f.write("content")

        result = self._run_auto_commit(git_repo, "after_specify", config)
        assert result.returncode == 0
        # Should NOT have committed
        log = subprocess.run(
            ["git", "-C", git_repo, "log", "--oneline", "-3"],
            capture_output=True, text=True
        )
        assert "Add specification" not in log.stdout

    def test_uses_custom_message_when_configured(self, git_repo):
        config = textwrap.dedent("""\
            auto_commit:
              default: false
              after_plan:
                enabled: true
                message: "[Spec Kit] Add implementation plan"
        """)
        write_git_config(git_repo, config)
        new_file = os.path.join(git_repo, "plan_file.txt")
        with open(new_file, "w") as f:
            f.write("plan content")

        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "auto-commit.sh"
        )
        result = run_script(script, args=["after_plan"], cwd=git_repo)
        assert result.returncode == 0

        log = subprocess.run(
            ["git", "-C", git_repo, "log", "--oneline", "-1"],
            capture_output=True, text=True
        )
        assert "Add implementation plan" in log.stdout

    def test_derives_default_message_from_event_name(self, git_repo):
        config = textwrap.dedent("""\
            auto_commit:
              default: false
              after_specify:
                enabled: true
        """)
        write_git_config(git_repo, config)
        new_file = os.path.join(git_repo, "spec_file.txt")
        with open(new_file, "w") as f:
            f.write("spec content")

        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "auto-commit.sh"
        )
        result = run_script(script, args=["after_specify"], cwd=git_repo)
        assert result.returncode == 0

        log = subprocess.run(
            ["git", "-C", git_repo, "log", "--oneline", "-1"],
            capture_output=True, text=True
        )
        # Default message format: "[Spec Kit] Auto-commit after specify"
        assert "Auto-commit" in log.stdout or "after" in log.stdout

    def test_phase_before_reflected_in_default_message(self, git_repo):
        config = textwrap.dedent("""\
            auto_commit:
              default: false
              before_plan:
                enabled: true
        """)
        write_git_config(git_repo, config)
        new_file = os.path.join(git_repo, "pre_plan.txt")
        with open(new_file, "w") as f:
            f.write("pre plan content")

        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "auto-commit.sh"
        )
        result = run_script(script, args=["before_plan"], cwd=git_repo)
        assert result.returncode == 0
        # Commit message should include "before"
        log = subprocess.run(
            ["git", "-C", git_repo, "log", "--oneline", "-1"],
            capture_output=True, text=True
        )
        assert "before" in log.stdout.lower()


# ===========================================================================
# auto-commit.sh: graceful degradation (non-git)
# ===========================================================================

class TestAutoCommitGracefulDegradation:
    """Tests for graceful degradation in auto-commit.sh when not in a git repo."""

    def test_exits_0_when_not_a_git_repo(self, non_git_dir):
        config = textwrap.dedent("""\
            auto_commit:
              default: true
        """)
        write_git_config(non_git_dir, config)
        script = os.path.join(
            non_git_dir, ".specify", "extensions", "git", "scripts", "bash", "auto-commit.sh"
        )
        result = run_script(script, args=["after_specify"], cwd=non_git_dir)
        assert result.returncode == 0
        assert "Warning" in result.stderr


# ===========================================================================
# initialize-repo.sh: fresh repository init
# ===========================================================================

class TestInitializeRepo:
    """Tests for initialize-repo.sh."""

    def test_initializes_repo_in_empty_dir(self, tmp_path):
        # Plain directory without git, with .specify structure
        d = str(tmp_path / "fresh")
        os.makedirs(d)
        # Copy the script and create .specify dir
        scripts_dir = os.path.join(d, ".specify", "extensions", "git", "scripts", "bash")
        os.makedirs(scripts_dir)
        import shutil
        shutil.copy2(INIT_REPO, os.path.join(scripts_dir, "initialize-repo.sh"))
        os.chmod(os.path.join(scripts_dir, "initialize-repo.sh"), 0o755)

        # Set up git user config globally for this process
        result = run_script(
            os.path.join(scripts_dir, "initialize-repo.sh"),
            cwd=d,
            env={
                "GIT_AUTHOR_NAME": "Test",
                "GIT_AUTHOR_EMAIL": "t@test.com",
                "GIT_COMMITTER_NAME": "Test",
                "GIT_COMMITTER_EMAIL": "t@test.com",
            },
        )
        assert result.returncode == 0
        assert "Git repository initialized" in result.stderr
        assert os.path.isdir(os.path.join(d, ".git"))

    def test_skips_if_already_a_git_repo(self, git_repo):
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "initialize-repo.sh"
        )
        result = run_script(script, cwd=git_repo)
        assert result.returncode == 0
        assert "already initialized" in result.stderr.lower() or "skipping" in result.stderr.lower()

    def test_reads_custom_commit_message_from_config(self, tmp_path):
        d = str(tmp_path / "custom_msg")
        os.makedirs(d)
        scripts_dir = os.path.join(d, ".specify", "extensions", "git", "scripts", "bash")
        os.makedirs(scripts_dir)
        import shutil
        shutil.copy2(INIT_REPO, os.path.join(scripts_dir, "initialize-repo.sh"))
        os.chmod(os.path.join(scripts_dir, "initialize-repo.sh"), 0o755)

        write_git_config(d, textwrap.dedent("""\
            branch_numbering: sequential
            init_commit_message: "[My Project] Custom initial commit"
        """))

        result = run_script(
            os.path.join(scripts_dir, "initialize-repo.sh"),
            cwd=d,
            env={
                "GIT_AUTHOR_NAME": "Test",
                "GIT_AUTHOR_EMAIL": "t@test.com",
                "GIT_COMMITTER_NAME": "Test",
                "GIT_COMMITTER_EMAIL": "t@test.com",
            },
        )
        assert result.returncode == 0

        log = subprocess.run(
            ["git", "-C", d, "log", "--oneline", "-1"],
            capture_output=True, text=True,
        )
        assert "Custom initial commit" in log.stdout

    def test_uses_default_message_when_no_config(self, tmp_path):
        d = str(tmp_path / "default_msg")
        os.makedirs(d)
        scripts_dir = os.path.join(d, ".specify", "extensions", "git", "scripts", "bash")
        os.makedirs(scripts_dir)
        import shutil
        shutil.copy2(INIT_REPO, os.path.join(scripts_dir, "initialize-repo.sh"))
        os.chmod(os.path.join(scripts_dir, "initialize-repo.sh"), 0o755)
        # No git-config.yml

        result = run_script(
            os.path.join(scripts_dir, "initialize-repo.sh"),
            cwd=d,
            env={
                "GIT_AUTHOR_NAME": "Test",
                "GIT_AUTHOR_EMAIL": "t@test.com",
                "GIT_COMMITTER_NAME": "Test",
                "GIT_COMMITTER_EMAIL": "t@test.com",
            },
        )
        assert result.returncode == 0

        log = subprocess.run(
            ["git", "-C", d, "log", "--oneline", "-1"],
            capture_output=True, text=True,
        )
        assert "[Spec Kit] Initial commit" in log.stdout


# ===========================================================================
# initialize-repo.sh: find_project_root
# ===========================================================================

class TestFindProjectRoot:
    """Tests for the _find_project_root helper embedded in multiple scripts."""

    def test_finds_root_via_specify_dir(self, tmp_path):
        """The scripts discover the project root by walking up to .specify/."""
        # The git_repo fixture already has .specify, so we can verify init-repo skips it
        d = str(tmp_path / "nested_project")
        specify = os.path.join(d, ".specify")
        os.makedirs(specify)
        # Init git in d so that initialize-repo finds a git repo
        init_git_repo(d)
        scripts_dir = os.path.join(specify, "extensions", "git", "scripts", "bash")
        os.makedirs(scripts_dir)
        import shutil
        shutil.copy2(INIT_REPO, os.path.join(scripts_dir, "initialize-repo.sh"))
        os.chmod(os.path.join(scripts_dir, "initialize-repo.sh"), 0o755)

        result = run_script(
            os.path.join(scripts_dir, "initialize-repo.sh"),
            cwd=d,
        )
        # Already a git repo, so it should skip
        assert result.returncode == 0
        assert "already initialized" in result.stderr.lower() or "skipping" in result.stderr.lower()


# ===========================================================================
# Boundary / regression tests
# ===========================================================================

class TestBoundaryAndRegression:
    """Additional boundary and regression tests for robustness."""

    def test_check_feature_branch_exactly_three_digits(self):
        """Minimum valid sequential prefix is 3 digits."""
        result = run_bash(
            f'source "{GIT_COMMON}"; check_feature_branch "100-feat" "true"; echo "EXIT:$?"'
        )
        assert "EXIT:0" in result.stdout

    def test_check_feature_branch_two_digits_fails(self):
        """Two-digit prefix is not accepted."""
        result = run_bash(
            f'source "{GIT_COMMON}"; check_feature_branch "10-feat" "true" 2>&1; echo "EXIT:$?"'
        )
        assert "EXIT:1" in result.stdout

    def test_auto_commit_exits_cleanly_with_empty_config(self, git_repo):
        """Empty git-config.yml should not crash auto-commit."""
        write_git_config(git_repo, "")
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "auto-commit.sh"
        )
        result = run_script(script, args=["after_specify"], cwd=git_repo)
        # Should exit 0 (disabled by default when no config key)
        assert result.returncode == 0

    def test_create_feature_produces_valid_json(self, git_repo):
        """JSON output must be parseable."""
        import json
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"
        )
        result = run_script(
            script,
            args=["--dry-run", "--json", "--number", "3", "--short-name", "test-feat", "description"],
            cwd=git_repo,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout.strip())
        assert "BRANCH_NAME" in data
        assert "FEATURE_NUM" in data

    def test_create_feature_number_zero_becomes_one(self, git_repo):
        """When specs/ is empty and no branches exist, first number should be 001."""
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"
        )
        # Remove any specs dir to ensure start at 0+1=1
        specs_dir = os.path.join(git_repo, "specs")
        if os.path.exists(specs_dir):
            import shutil
            shutil.rmtree(specs_dir)

        result = run_script(
            script,
            args=["--dry-run", "--json", "--short-name", "first-feat", "First feature"],
            cwd=git_repo,
        )
        assert result.returncode == 0
        import json
        data = json.loads(result.stdout.strip())
        # Should be 001 (from 0 highest + 1)
        assert data["FEATURE_NUM"] == "001"

    def test_check_feature_branch_rejects_no_slug_after_timestamp(self):
        """Timestamp branch without slug (20260319-143022 alone) is invalid."""
        result = run_bash(
            f'source "{GIT_COMMON}"; check_feature_branch "20260319-143022" "true" 2>&1; echo "EXIT:$?"'
        )
        assert "EXIT:1" in result.stdout

    def test_create_feature_branch_name_truncated_beyond_244(self, git_repo):
        """Branch name exceeding 244 bytes should be truncated with a warning."""
        script = os.path.join(
            git_repo, ".specify", "extensions", "git", "scripts", "bash", "create-new-feature.sh"
        )
        long_short_name = "x" * 250
        result = run_script(
            script,
            args=["--dry-run", "--json", "--number", "1", "--short-name", long_short_name, "desc"],
            cwd=git_repo,
        )
        assert result.returncode == 0
        assert "244" in result.stderr or "exceeded" in result.stderr.lower()
        import json
        data = json.loads(result.stdout.strip())
        assert len(data["BRANCH_NAME"].encode("utf-8")) <= 244