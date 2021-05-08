# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -
• `{i}update`
    See changelogs if any update is available.

• `{i}update now`
    (Force)Update your bots to the latest version.
"""
import asyncio
import sys
from os import execl, path, remove

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from . import HELP, get_string, ultroid_version

UPSTREAM_REPO_URL = "https://github.com/TeamUltroid/Ultroid"
requirements_path = path.join(
    path.dirname(path.dirname(path.dirname(__file__))),
    "requirements.txt",
)


async def gen_chlog(repo, diff):
    ac_br = repo.active_branch.name
    ch_log = tldr_log = ""
    ch = f"<b>Ultroid {ultroid_version} updates for <a href={UPSTREAM_REPO_URL}/tree/{ac_br}>[{ac_br}]</a>:</b>"
    ch_tl = f"Ultroid {ultroid_version} updates for {ac_br}:"
    d_form = "%d/%m/%y || %H:%M"
    for c in repo.iter_commits(diff):
        ch_log += f"\n\n💬 <b>{c.count()}</b> 🗓 <b>[{c.committed_datetime.strftime(d_form)}]</b>\n<b><a href={UPSTREAM_REPO_URL.rstrip('/')}/commit/{c}>[{c.summary}]</a></b> 👨‍💻 <code>{c.author}</code>"
        tldr_log += f"\n\n💬 {c.count()} 🗓 [{c.committed_datetime.strftime(d_form)}]\n[{c.summary}] 👨‍💻 {c.author}"
    if ch_log:
        return str(ch + ch_log), str(ch_tl + tldr_log)
    else:
        return ch_log, tldr_log


async def updateme_requirements():
    reqs = str(requirements_path)
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join([sys.executable, "-m", "pip", "install", "-r", reqs]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


@ultroid_cmd(
    pattern="update ?(.*)",
)
async def upstream(ups):
    pagal = await eor(ups, get_string("upd_1"))
    conf = ups.pattern_match.group(1)
    off_repo = UPSTREAM_REPO_URL
    try:
        txt = get_string("upd_2")
        repo = Repo()
    except NoSuchPathError as error:
        await eod(pagal, f"{txt}\n`directory {error} is not found`", time=10)
        repo.__del__()
        return
    except GitCommandError as error:
        await eod(pagal, f"{txt}\n`Early failure! {error}`", time=10)
        repo.__del__()
        return
    except InvalidGitRepositoryError as error:
        if conf != "now":
            await eod(
                pagal,
                f"**Unfortunately, the directory {error} does not seem to be a git repository.Or Maybe it just needs a sync verification with {GIT_REPO_NAME} But we can fix that by force updating the userbot using** `.update now.`",
                time=30,
            )
            return
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        repo.create_head("dev", origin.refs.dev)
        repo.heads.dev.set_tracking_branch(origin.refs.dev)
        repo.heads.dev.checkout(True)
    ac_br = repo.active_branch.name
    try:
        repo.create_remote("upstream", off_repo)
    except BaseException:
        pass
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)
    changelog, tl_chnglog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    if "now" not in conf:
        if changelog:
            changelog_str = (
                changelog + f"\n\nUse <code>{hndlr}update now</code> to update!"
            )
            tldr_str = tl_chnglog + f"\n\nUse {hndlr}update now to update!"
            if len(changelog_str) > 4096:
                await eor(pagal, get_string("upd_4"))
                file = open(f"ultroid_updates.txt", "w+")
                file.write(tldr_str)
                file.close()
                await ups.client.send_file(
                    ups.chat_id,
                    f"ultroid_updates.txt",
                    caption=get_string("upd_5").format(hndlr),
                    reply_to=ups.id,
                )
                remove(f"ultroid_updates.txt")
                return
            else:
                return await eod(pagal, changelog_str, parse_mode="html")
        else:
            await eod(
                pagal,
                get_string("upd_7").format(ac_br, UPSTREAM_REPO_URL, ac_br),
                time=10,
            )
            repo.__del__()
            return
    if Var.HEROKU_API is not None:
        import heroku3

        heroku = heroku3.from_key(Var.HEROKU_API)
        heroku_app = None
        heroku_applications = heroku.apps()
        if not Var.HEROKU_APP_NAME:
            await eod(
                pagal,
                "`Please set up the `HEROKU_APP_NAME` variable to be able to update userbot.`",
                time=10,
            )
            repo.__del__()
            return
        for app in heroku_applications:
            if app.name == Var.HEROKU_APP_NAME:
                heroku_app = app
                break
        if heroku_app is None:
            await eod(
                pagal,
                f"{txt}\n`Invalid Heroku credentials for updating userbot dyno.`",
                time=10,
            )
            repo.__del__()
            return
        await eor(
            pagal,
            "`Userbot dyno build in progress, please wait for it to complete.`",
        )
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://",
            "https://api:" + Var.HEROKU_API + "@",
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec=f"HEAD:refs/heads/{ac_br}", force=True)
        except GitCommandError as error:
            await eod(pagal, f"{txt}\n`Here is the error log:\n{error}`", time=10)
            repo.__del__()
            return
        await eod(pagal, "`Successfully Updated!\nRestarting, please wait...`", time=60)
    else:
        # Classic Updater, pretty straightforward.
        try:
            ups_rem.pull(ac_br)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await updateme_requirements()
        await eod(
            pagal,
            "`Successfully Updated!\nBot is restarting... Wait for a second!`",
        )
        # Spin a new instance of bot
        execl(sys.executable, sys.executable, "-m", "pyUltroid")
        return


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
