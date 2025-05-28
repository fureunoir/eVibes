import {createRouter, createWebHistory, RouterView} from 'vue-router'
import HomePage from "@/pages/home-page.vue";
import translation from "@/core/helpers/translations.js";
import {APP_NAME} from "@/config/index.js";
import NewPasswordForm from "@/components/forms/new-password-form.vue";
import BlogPage from "@/pages/blog-page.vue";
import PostPage from "@/pages/post-page.vue";
import ProfilePage from "@/pages/profile-page.vue";
import {useAuthStore} from "@/stores/auth.js";
import RegisterForm from "@/components/forms/register-form.vue";
import LoginForm from "@/components/forms/login-form.vue";
import ResetPasswordForm from "@/components/forms/reset-password-form.vue";
import StorePage from "@/pages/store-page.vue";
import ProductPage from "@/pages/product-page.vue";

const routes = [
  {
    path: '/:locale?',
    component: RouterView,
    beforeEnter: translation.routeMiddleware,
    children: [
      {
        path: '',
        name: 'home',
        component: HomePage,
        meta: {
          title: "Home"
        }
      },
      {
        path: 'activate-user',
        name: 'activate-user',
        component: HomePage,
        meta: {
          title: 'Home'
        }
      },
      {
        path: 'reset-password',
        name: 'reset-password',
        component: NewPasswordForm,
        meta: {
          title: 'New Password'
        }
      },
      {
        path: 'register',
        name: 'register',
        component: RegisterForm,
        meta: {
          title: 'Register',
          requiresGuest: true
        }
      },
      {
        path: 'login',
        name: 'login',
        component: LoginForm,
        meta: {
          title: 'Login',
          requiresGuest: true
        }
      },
      {
        path: 'forgot-password',
        name: 'forgot-password',
        component: ResetPasswordForm,
        meta: {
          title: 'Forgot Password',
          requiresGuest: true
        }
      },
      {
        path: 'blog',
        name: 'blog',
        component: BlogPage,
        meta: {
          title: 'Blog'
        }
      },
      {
        path: 'blog/post/:postSlug',
        name: 'blog-post',
        component: PostPage,
        meta: {
          title: 'Post'
        }
      },
      {
        path: 'store',
        name: 'store',
        component: StorePage,
        meta: {
          title: 'Store'
        }
      },
      {
        path: 'product/:productSlug',
        name: 'product',
        component: ProductPage,
        meta: {
          title: 'Product'
        }
      },
      {
        path: 'profile',
        name: 'profile',
        component: ProfilePage,
        meta: {
          title: 'Profile',
          requiresAuth: true
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    document.querySelector('#top').scrollIntoView({ behavior: 'smooth' })
    return {
      top: 0,
      left: 0,
      behavior: 'smooth'
    }
  }
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.accessToken

  document.title = to.meta.title ? `${APP_NAME} | ` + to.meta?.title : APP_NAME

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({
      name: 'home',
      query: { redirect: to.fullPath }
    });
  }

  if (to.meta.requiresGuest && isAuthenticated) {
    return next({ name: 'home' });
  }

  next();
})

export default router