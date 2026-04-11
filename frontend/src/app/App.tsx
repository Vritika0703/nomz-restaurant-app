import { useEffect, useLayoutEffect, useState } from 'react';
import { apiFetch } from './api';
import { motion } from 'motion/react';
import { SignIn } from './components/SignIn';
import { SignUp } from './components/SignUp';
import { Home } from './components/Home';
import { UserHome } from './components/UserHome';
import { RestaurantProfile } from './components/RestaurantProfile';
import { UserProfile } from './components/UserProfile';
import { Messages } from './components/Messages';
import { Map } from './components/Map';
import { PhotoManagement } from './components/PhotoManagement';
import { AdminDashboard } from './components/AdminDashboard';
import { AdminRestaurantAccounts } from './components/AdminRestaurantAccounts';
import { AdminModeration } from './components/AdminModeration';
import { AdminPendingApprovals } from './components/AdminPendingApprovals';
import { AdminManageUsers } from './components/AdminManageUsers';
import { AdminLogs } from './components/AdminLogs';
import { PasswordResetForm } from './components/PasswordResetForm';
import { PasswordResetDone } from './components/PasswordResetDone';
import { PasswordResetConfirm } from './components/PasswordResetConfirm';
import { PasswordResetComplete } from './components/PasswordResetComplete';
import { ManageActivation } from './components/ManageActivation';
import { TwoFactorAuth } from './components/TwoFactorAuth';
import { ClaimRestaurant } from './components/ClaimRestaurant';
import { RestaurantDetail } from './components/RestaurantDetail';
import { AddReview } from './components/AddReview';
import { ReportContent } from './components/ReportContent';
import { SearchResults } from './components/SearchResults';
import { Recommendations } from './components/Recommendations';
import { RestaurantForm } from './components/RestaurantForm';

type View = 'opening' | 'home' | 'signin' | 'signup' | 'userhome' | 'restaurantprofile' | 'userprofile' | 'messages' | 'map' | 'restaurantmap' | 'photomanagement' | 'admin' | 'adminmoderation' | 'adminapprovals' | 'adminapproved' | 'adminrejected' | 'adminusers' | 'adminlogs' | 'adminmap' | 'passwordreset' | 'passwordresetdone' | 'passwordresetconfirm' | 'passwordresetcomplete' | 'manageactivation' | 'twofactorauth' | 'claimrestaurant' | 'restaurantdetail' | 'addreview' | 'reportcontent' | 'searchresults' | 'recommendations' | 'restaurantform';

interface UserData {
  username: string;
  accountType: 'diner' | 'restaurant' | 'admin';
}

export default function App() {
  const [view, setView] = useState<View>('opening');
  const [showClickToStart, setShowClickToStart] = useState(false);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [resetUid, setResetUid] = useState<string | null>(null);
  const [resetToken, setResetToken] = useState<string | null>(null);
  const [selectedRestaurantId, setSelectedRestaurantId] = useState<number | null>(null);
  const [selectedRestaurantName, setSelectedRestaurantName] = useState<string>('');
  const [reportTarget, setReportTarget] = useState<{ type: 'review' | 'user'; id: number } | null>(null);
  const [previousView, setPreviousView] = useState<View>('map');
  const [searchQuery, setSearchQuery] = useState('');
  const [pendingMessageStart, setPendingMessageStart] = useState<{ id: number; name: string } | null>(null);
  /** True when user opened the app with `?admin` — same Log In screen, plus security code (AdminLoginForm). */
  const [signInAdminPortal, setSignInAdminPortal] = useState(false);

  useEffect(() => {
    if (view !== 'messages') {
      setPendingMessageStart(null);
    }
  }, [view]);

  useLayoutEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const uidParam = params.get('resetUid');
    const tokenParam = params.get('resetToken');
    if (uidParam && tokenParam) {
      setResetUid(uidParam);
      setResetToken(tokenParam);
      setView('passwordresetconfirm');
      window.history.replaceState({}, '', window.location.pathname);
      return;
    }
    if (params.has('admin')) {
      params.delete('admin');
      const qs = params.toString();
      window.history.replaceState({}, '', qs ? `${window.location.pathname}?${qs}` : window.location.pathname);
      setSignInAdminPortal(true);
      setView('signin');
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const r = await apiFetch('/api/auth/session/');
        const data = await r.json();
        if (cancelled || !data.authenticated) return;
        let accountType: UserData['accountType'] = 'diner';
        if (data.is_staff) accountType = 'admin';
        else if (data.role === 'restaurant') accountType = 'restaurant';
        setUserData({ username: data.username, accountType });
      } catch {
        /* offline or CORS */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleAnimationEnd = () => {
    setShowClickToStart(true);
  };

  const handleClick = () => {
    if (view === 'opening' && showClickToStart) {
      setView('home');
    }
  };

  const handleSignInClick = () => {
    setSignInAdminPortal(false);
    setView('signin');
  };

  const handleSignUpClick = () => {
    setView('signup');
  };

  const handleBackToHome = () => {
    setSignInAdminPortal(false);
    setView('home');
  };

  const handleSignIn = (accountType: 'diner' | 'restaurant' | 'admin', username: string) => {
    setSignInAdminPortal(false);
    setUserData({ username, accountType });
    if (accountType === 'diner') setView('userhome');
    else if (accountType === 'restaurant') setView('restaurantprofile');
    else setView('admin');
  };

  const handleSignUp = (accountType: 'diner' | 'restaurant' | 'admin', username: string) => {
    setUserData({ username, accountType });
    if (accountType === 'diner') setView('userhome');
    else if (accountType === 'restaurant') setView('restaurantprofile');
    else setView('admin');
  };

  const handleLogout = async () => {
    try {
      await apiFetch('/api/auth/logout/', { method: 'POST' });
    } catch {
      /* ignore */
    }
    setUserData(null);
    setView('home');
  };

  const handleViewProfile = () => {
    setView('userprofile');
  };

  const handleBackToUserHome = () => {
    setView('userhome');
  };

  const handleViewMessages = () => {
    setView('messages');
  };

  const handleNavigateMap = () => {
    setView('map');
  };

  const handlePhotoManagement = () => {
    setView('photomanagement');
  };

  const handleViewModeration = () => {
    setView('adminmoderation');
  };

  const handleViewPendingApprovals = () => {
    setView('adminapprovals');
  };

  const handleViewManageUsers = () => {
    setView('adminusers');
  };

  const handleViewAdminLogs = () => {
    setView('adminlogs');
  };

  const handleViewApprovedAccounts = () => {
    setView('adminapproved');
  };

  const handleViewRejectedAccounts = () => {
    setView('adminrejected');
  };

  const handleAdminBack = () => {
    setView('admin');
  };

  const handleAdminMapBack = () => {
    setView('admin');
  };

  const handleAdminMapAccess = () => {
    setView('adminmap');
  };

  const handleForgotPassword = () => {
    setView('passwordreset');
  };

  const handlePasswordResetSubmit = () => {
    setView('passwordresetdone');
  };

  const handlePasswordResetConfirm = () => {
    setView('passwordresetconfirm');
  };

  const handlePasswordResetComplete = () => {
    setView('passwordresetcomplete');
  };

  const handlePasswordResetToLogin = () => {
    setSignInAdminPortal(false);
    setView('signin');
  };

  const handleManageActivation = () => {
    setView('manageactivation');
  };

  const handleActivationToggle = () => {
    setView('restaurantprofile');
  };

  const handleTwoFactorAuth = () => {
    setView('twofactorauth');
  };

  const handleTwoFactorVerify = (data: { username: string; role?: string; is_staff?: boolean }) => {
    let accountType: UserData['accountType'] = 'diner';
    if (data.is_staff) accountType = 'admin';
    else if (data.role === 'restaurant') accountType = 'restaurant';
    setUserData({ username: data.username, accountType });
    if (accountType === 'restaurant') {
      setView('restaurantprofile');
    } else if (accountType === 'admin') {
      setView('admin');
    } else {
      setView('userhome');
    }
  };

  const handleClaimListing = () => {
    setView('claimrestaurant');
  };

  const handleUserSearch = (q: string) => {
    setSearchQuery(q);
    setView('searchresults');
  };

  const handleBackFromSearch = () => {
    setView('userhome');
  };

  const handleOpenRecommendations = () => {
    setView('recommendations');
  };

  const handleBackFromRecommendations = () => {
    setView('userhome');
  };

  const handleRestaurantForm = () => {
    setView('restaurantform');
  };

  const handleBackFromRestaurantForm = () => {
    setView('restaurantprofile');
  };

  const handleBackFromClaimListing = () => {
    setView('restaurantprofile');
  };

  const handleSelectRestaurant = (id: number) => {
    setSelectedRestaurantId(id);
    setPreviousView(view);
    setView('restaurantdetail');
  };

  const handleWriteReview = (restaurantId: number) => {
    setSelectedRestaurantId(restaurantId);
    setSelectedRestaurantName('');
    setView('addreview');
  };

  const handleReportReview = (reviewId: number) => {
    setReportTarget({ type: 'review', id: reviewId });
    setView('reportcontent');
  };

  const handleReportOwner = (userId: number) => {
    setReportTarget({ type: 'user', id: userId });
    setView('reportcontent');
  };

  const handleBackFromDetail = () => {
    setView(previousView);
  };

  const handleReviewSuccess = () => {
    // Go back to the restaurant detail to see the new review
    setView('restaurantdetail');
  };

  const handleReportSuccess = () => {
    setView('restaurantdetail');
  };

  if (view === 'reportcontent' && reportTarget) {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <ReportContent
          contentType={reportTarget.type}
          contentId={reportTarget.id}
          onBack={() => setView('restaurantdetail')}
          onSuccess={handleReportSuccess}
        />
      </div>
    );
  }

  if (view === 'addreview' && selectedRestaurantId) {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AddReview
          restaurantId={selectedRestaurantId}
          restaurantName={selectedRestaurantName}
          onBack={() => setView('restaurantdetail')}
          onSuccess={handleReviewSuccess}
        />
      </div>
    );
  }

  if (view === 'restaurantdetail' && selectedRestaurantId) {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <RestaurantDetail
          restaurantId={selectedRestaurantId}
          onBack={handleBackFromDetail}
          onWriteReview={handleWriteReview}
          onReportReview={handleReportReview}
          onReportOwner={handleReportOwner}
          onStartConversation={
            userData?.accountType === 'diner'
              ? (id, name) => {
                  setPendingMessageStart({ id, name });
                  setView('messages');
                }
              : undefined
          }
        />
      </div>
    );
  }

  if (view === 'claimrestaurant') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <ClaimRestaurant onBack={handleBackFromClaimListing} />
      </div>
    );
  }

  if (view === 'adminapproved') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AdminRestaurantAccounts listKind="approved" onBack={handleAdminBack} />
      </div>
    );
  }

  if (view === 'adminrejected') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AdminRestaurantAccounts listKind="rejected" onBack={handleAdminBack} />
      </div>
    );
  }

  if (view === 'adminlogs') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AdminLogs onBack={handleAdminBack} />
      </div>
    );
  }

  if (view === 'adminusers') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AdminManageUsers onBack={handleAdminBack} />
      </div>
    );
  }

  if (view === 'adminapprovals') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AdminPendingApprovals onBack={handleAdminBack} />
      </div>
    );
  }

  if (view === 'adminmoderation') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AdminModeration onBack={handleAdminBack} />
      </div>
    );
  }

  if (view === 'admin') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AdminDashboard 
          onLogout={handleLogout}
          onNavigateMap={handleAdminMapAccess}
          onViewModeration={handleViewModeration}
          onViewPendingApprovals={handleViewPendingApprovals}
          onViewPendingUsers={handleViewManageUsers}
          onViewLogs={handleViewAdminLogs}
          onViewApprovedAccounts={handleViewApprovedAccounts}
          onViewRejectedAccounts={handleViewRejectedAccounts}
        />
      </div>
    );
  }

  if (view === 'adminmap') {
    return (
      <div className="min-h-screen w-screen overflow-auto">
        <Map 
          onNavigateHome={handleAdminMapBack}
          onNavigateMessages={handleAdminMapBack}
          onNavigateProfile={handleAdminMapBack}
          onLogout={handleLogout}
          isAdmin={true}
          onSelectRestaurant={handleSelectRestaurant}
        />
      </div>
    );
  }

  if (view === 'photomanagement') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <PhotoManagement onBack={() => setView('restaurantprofile')} />
      </div>
    );
  }

  if (view === 'map') {
    return (
      <div className="min-h-screen w-screen overflow-auto">
        <Map 
          onNavigateHome={handleBackToUserHome}
          onNavigateMessages={handleViewMessages}
          onNavigateProfile={handleViewProfile}
          onLogout={handleLogout}
          isAdmin={false}
          onSelectRestaurant={handleSelectRestaurant}
        />
      </div>
    );
  }

  if (view === 'messages') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <Messages 
          onNavigateMap={handleNavigateMap}
          onNavigateHome={userData?.accountType === 'restaurant' ? () => setView('restaurantprofile') : handleBackToUserHome}
          onNavigateProfile={handleViewProfile}
          onLogout={handleLogout}
          accountType={userData?.accountType === 'restaurant' ? 'Restaurant' : 'Diner'}
          pendingStartRestaurantId={pendingMessageStart?.id ?? null}
          pendingStartRestaurantName={pendingMessageStart?.name ?? ''}
          onConsumedPendingStart={() => setPendingMessageStart(null)}
        />
      </div>
    );
  }

  if (view === 'userprofile') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <UserProfile 
          onBack={handleBackToUserHome} 
          onViewMessages={handleViewMessages}
          onNavigateMap={handleNavigateMap}
          onNavigateHome={() => setView('home')}
          username={userData?.username || 'Diner'} 
        />
      </div>
    );
  }

  if (view === 'restaurantform') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <RestaurantForm onBack={handleBackFromRestaurantForm} />
      </div>
    );
  }

  if (view === 'recommendations' && userData?.accountType === 'diner') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <Recommendations
          onBack={handleBackFromRecommendations}
          onSelectRestaurant={handleSelectRestaurant}
          onNavigateMap={handleNavigateMap}
          onNavigateMessages={handleViewMessages}
          onNavigateProfile={handleViewProfile}
          onOpenPreferences={handleViewProfile}
          onLogout={handleLogout}
          username={userData.username}
        />
      </div>
    );
  }

  if (view === 'searchresults' && userData?.accountType === 'diner') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <SearchResults
          initialQuery={searchQuery}
          onBack={handleBackFromSearch}
          onSelectRestaurant={handleSelectRestaurant}
          onNavigateMap={handleNavigateMap}
          onNavigateMessages={handleViewMessages}
          onNavigateProfile={handleViewProfile}
          onLogout={handleLogout}
          username={userData.username}
        />
      </div>
    );
  }

  if (view === 'userhome') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <UserHome 
          onLogout={handleLogout} 
          onViewProfile={handleViewProfile}
          onViewMessages={handleViewMessages}
          onNavigateMap={handleNavigateMap}
          onSearch={handleUserSearch}
          onOpenRecommendations={handleOpenRecommendations}
          onSelectRestaurant={handleSelectRestaurant}
          username={userData?.username || 'Diner'} 
        />
      </div>
    );
  }

  if (view === 'restaurantprofile') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <RestaurantProfile 
          onLogout={handleLogout} 
          username={userData?.username || 'Restaurant'} 
          onNavigateMessages={handleViewMessages}
          onPhotoManagement={handlePhotoManagement}
          onNavigateMap={handleNavigateMap}
          onNavigateRestaurantMap={() => setView('restaurantmap')}
          onBack={() => setView('restaurantprofile')}
          onManageActivation={handleManageActivation}
          onClaimListing={handleClaimListing}
          onRestaurantForm={handleRestaurantForm}
        />
      </div>
    );
  }

  if (view === 'restaurantmap') {
    return (
      <div className="min-h-screen w-screen overflow-auto">
        <Map 
          onNavigateHome={() => setView('restaurantprofile')}
          onNavigateMessages={handleViewMessages}
          onNavigateProfile={() => setView('restaurantprofile')}
          onLogout={handleLogout}
          isAdmin={false}
          onSelectRestaurant={handleSelectRestaurant}
        />
      </div>
    );
  }

  if (view === 'twofactorauth') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <TwoFactorAuth 
          onBack={handleSignInClick}
          onVerify={handleTwoFactorVerify}
          onResend={() => console.log('Resending 2FA code')}
        />
      </div>
    );
  }

  if (view === 'manageactivation') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <ManageActivation 
          onBack={handleActivationToggle}
          onToggle={handleActivationToggle}
        />
      </div>
    );
  }

  if (view === 'passwordresetcomplete') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <PasswordResetComplete onLoginClick={handlePasswordResetToLogin} />
      </div>
    );
  }

  if (view === 'passwordresetconfirm') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <PasswordResetConfirm 
          onBack={handlePasswordResetToLogin} 
          onSubmit={handlePasswordResetComplete}
          isValidLink={true}
          uid={resetUid ?? undefined}
          token={resetToken ?? undefined}
        />
      </div>
    );
  }

  if (view === 'passwordresetdone') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <PasswordResetDone onBack={handlePasswordResetToLogin} />
      </div>
    );
  }

  if (view === 'passwordreset') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <PasswordResetForm 
          onBack={handleBackToHome} 
          onSubmit={handlePasswordResetSubmit}
        />
      </div>
    );
  }

  if (view === 'signin') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <SignIn 
          onBackClick={handleBackToHome} 
          onSignIn={handleSignIn}
          onForgotPassword={handleForgotPassword}
          onTwoFactorRequired={handleTwoFactorAuth}
          adminPortal={signInAdminPortal}
        />
      </div>
    );
  }

  if (view === 'signup') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <SignUp onBackClick={handleBackToHome} onSignUp={handleSignUp} />
      </div>
    );
  }

  if (view === 'home') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <Home 
          onSignInClick={handleSignInClick} 
          onSignUpClick={handleSignUpClick}
        />
      </div>
    );
  }

  return (
    <div 
      className="size-full flex items-center justify-center cursor-pointer" 
      style={{ backgroundImage: 'radial-gradient(circle, #E06E7F, #FFF9F5)' }}
      onClick={handleClick}
    >
      <div className="flex flex-col items-center gap-2">
        <div className="flex items-center gap-2">
          {['n', 'o', 'm', 'z'].map((letter, index) => (
            <motion.span
              key={index}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ 
                opacity: 1, 
                scale: [0.5, 1.2, 1],
              }}
              transition={{
                duration: 0.8,
                delay: index * 0.15,
                ease: "easeOut"
              }}
              className="text-4xl text-white"
              style={{ 
                fontFamily: 'Montserrat, sans-serif',
                filter: 'drop-shadow(0 0 8px rgba(224, 110, 127, 0.6))'
              }}
            >
              {letter}
            </motion.span>
          ))}
        </div>
        
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{
            duration: 0.5,
            delay: 1.1,
            ease: "easeIn"
          }}
          onAnimationComplete={handleAnimationEnd}
          className="text-xs text-white"
          style={{ 
            fontFamily: 'Montserrat, sans-serif'
          }}
        >
          click to start
        </motion.p>
      </div>
    </div>
  );
}