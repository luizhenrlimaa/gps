def post_fork(server, worker):
    server.log.info("Worker spawned (post-fork) (pid: %s)", worker.pid)

def pre_fork(server, worker):
    server.log.info("Worker spawned (pre-fork) (pid: %s)", worker.pid)

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

    ## get traceback info
    import threading, sys, traceback
    id2name = {th.ident: th.name for th in threading.enumerate()}
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# Thread: %s(%d)" % (id2name.get(threadId,""),
            threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename,
                lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    worker.log.debug("\n".join(code))

def worker_abort(worker):
    import traceback, io
    debug_info = io.StringIO()
    debug_info.write("Traceback at time of timeout:\n")
    traceback.print_stack(file=debug_info)
    worker.log.critical(debug_info.getvalue())