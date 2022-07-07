from django.urls import reverse


class MenuObject:
    def __init__(self, order, slug, title, url='None', icon='fa-circle-o', visible=True, iframe=False, has_help=False,
            extra_info=None):
        self.order = order
        self.slug = slug
        self.title = title
        self.url = url
        self.icon = icon
        self.visible = visible
        self.iframe = iframe
        self.has_help = has_help
        self.extra_info = extra_info or {}


MENUS = [
    MenuObject(order=1, slug='dashboard.*', title="Dashboard", url=reverse("dashboard-index")),
    MenuObject(order=10, slug='dashboard.index', title="Dashboard Index", url=reverse("dashboard-index"), icon="fa-home"),

    # profile
    MenuObject(order=33, slug='profile.*', title="Profile", url=reverse("dashboard-profile"), visible=False),
    MenuObject(order=3301, slug='profile.user.*', title="User", icon='fa-user'),
    MenuObject(order=330101, slug='profile.user.personal_info', title="Personal Info", url=reverse("profile-personal-info"), icon='fa-task'),
    MenuObject(order=330101, slug='profile.user.password', title="Change Password", url=reverse("profile-password-change"), icon='fa-key'),
    MenuObject(order=330102, slug='profile.user.password_done', title="Change Password Done", url=reverse("profile-password-done"), icon='fa-key', visible=False),
    MenuObject(order=330103, slug='profile.user.avatar', title="Avatar", url=reverse("profile-avatar-update"), icon='fa-camera'),
    # config
    MenuObject(order=44, slug='config.*', title="Configuration", url=reverse("dashboard-config")),
    MenuObject(order=4402, slug='config.audit.*', title="Audit", icon='fa-user-secret'),
    MenuObject(order=440201, slug='config.audit.log', title="Audit log", url=reverse("audit-log-list"), icon='fa-database', has_help=False),
    MenuObject(order=4403, slug='config.users.*', title="Authorization", icon="fa-users"),
    MenuObject(order=44, slug='config.users.users', url=reverse('users-list'), title="Users", icon="fa-user"),
    MenuObject(order=4403, slug='config.users.roles', title="User Roles", url=reverse("users-role-list"), icon="fa-lock"),
    MenuObject(order=4404, slug='config.users.alunos', title="Alunos", url=reverse("aluno-list"),
               icon="fa-lock"),

    MenuObject(order=55, slug='registros.*', title="Registros", url=reverse("registros-dashboard")),
    MenuObject(order=5502, slug='registros.categoria.*', title="Categoria", icon='fa-certificate'),
    MenuObject(order=5504, slug='registros.aluno.*', title='Solicitações Aluno', icon='fa-send'),
    MenuObject(order=5505, slug='registros.secretaria.*', title='Solicitações Secretaria', icon='fa-send'),

    MenuObject(order=550201, slug='registros.categoria.categorias', title="Categoria", url=reverse("categoria-list"),
               icon='fa-database', has_help=False),
    MenuObject(order=550202, slug='registros.categoria.atividade', title="Atividade", url=reverse("atividade-list"),
               icon='fa-database', has_help=False),


    MenuObject(order=550401, slug='registros.aluno.solicitacoes', title='Minhas Solicitações',
               url=reverse('submicao-aluno-list'), icon='fa-database', has_help=False),
    MenuObject(order=770502, slug='registros.secretaria.abertas', title='Solicitações Abertas',
               url=reverse('submicao-list'), icon='fa-database', has_help=False),



    MenuObject(order=66, slug='certificados.*', title="Gestão Certificado", url=reverse("certificados-dashboard")),
    MenuObject(order=6602, slug='certificados.certificados.*', title="Categoria", icon='fa-certificate'),
    MenuObject(order=660201, slug='certificados.certificados.meus_certificados', title="Meus Certificados", url=reverse("certificado-list"),
               icon='fa-database', has_help=False),

    MenuObject(order=77, slug='sub.*', title='Solicitação', url=reverse("submissao-dashboard")),

]
