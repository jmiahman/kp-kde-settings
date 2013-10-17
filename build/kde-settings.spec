
%global rel 23
%global system_kde_theme_ver 18.91

Summary: Config files for kde
Name:    kde-settings
Version: 19
<<<<<<< HEAD
Release: %{rel}%{?dist}.2
=======
Release: %{rel}.2%{?dist}
>>>>>>> korora/k19

License: MIT
Url:     http://fedorahosted.org/kde-settings
Source0: https://fedorahosted.org/releases/k/d/kde-settings/%{name}-%{version}-%{rel}.tar.xz
Source1: COPYING
Patch0:  korora-kdesettings.patch
BuildArch: noarch

BuildRequires: kde-filesystem
BuildRequires: systemd

Requires: kde-filesystem
# /etc/pam.d/ ownership
Requires: pam
Requires: xdg-user-dirs
Requires: adwaita-cursor-theme
%if 0%{?fedora}
# for 11-fedora-kde-policy.rules
Requires: polkit-js-engine
%endif

Requires(post): coreutils sed

%description
%{summary}.

%package minimal
Summary: Minimal configuration files for KDE
Requires: %{name} = %{version}-%{release}
Requires: kde-workspace-ksplash-themes
Requires: xorg-x11-xinit
%description minimal
%{summary}.

%package kdm
Summary: Configuration files for kdm
# MinShowUID=-1 is only supported from 4.7.1-2 on
Requires: kdm >= 4.7.1-2
%if 0%{?fedora}
Requires: system-kdm-theme >= %{system_kde_theme_ver}
%else
Requires: redhat-logos >= 69.0.0
%endif
Requires: xorg-x11-xinit
Requires(pre): coreutils
Requires(post): coreutils grep sed
Requires(post): kde4-macros(api) = %{_kde4_macros_api}
%{?systemd_requires}
%description kdm
%{summary}.

%package ksplash
Summary: Configuration files for ksplash
Requires: %{name} = %{version}-%{release}
%if 0%{?fedora}
Requires: system-ksplash-theme >= %{system_kde_theme_ver}
%else
Requires: redhat-logos >= 69.0.0
%endif
%description ksplash 
%{summary}.

%package plasma
Summary: Configuration files for plasma 
Requires: %{name} = %{version}-%{release}
%if 0%{?fedora}
Requires: system-plasma-desktoptheme >= %{system_kde_theme_ver}
%else
Requires: redhat-logos >= 69.0.0
%endif
%description plasma 
%{summary}.

%package pulseaudio
Summary: Enable pulseaudio support in KDE
# nothing here to license
License: Public Domain
Requires: %{name} = %{version}-%{release}
Requires: pulseaudio
Requires: pulseaudio-module-x11
## kde3
Requires: alsa-plugins-pulseaudio
## kde4: -pulseaudio plugins are installed for all phonon backends by default
%description pulseaudio
%{summary}.

%package -n qt-settings
Summary: Configuration files for Qt 
# qt-graphicssystem.* scripts use lspci
Requires: pciutils
%description -n qt-settings
%{summary}.


%prep
%setup -q -n %{name}-%{version}-%{rel}
%patch0 -p1

%build
# Intentionally left blank.  Nothing to see here.


%install
mkdir -p %{buildroot}{%{_datadir}/config,%{_sysconfdir}/kde/kdm}

tar cpf - . | tar --directory %{buildroot} -xvpf -

cp -p %{SOURCE1} .

# kdebase/kdm symlink
rm -rf   %{buildroot}%{_datadir}/config/kdm
ln -sf ../../../etc/kde/kdm %{buildroot}%{_datadir}/config/kdm

# own these
mkdir -p %{buildroot}%{_localstatedir}/lib/kdm
mkdir -p %{buildroot}%{_localstatedir}/run/{kdm,xdmctl}

# rhel stuff
%if 0%{?rhel}
rm -rf %{buildroot}%{_sysconfdir}/kde/env/fedora-bookmarks.sh \
       %{buildroot}%{_prefix}/lib/rpm \
       %{buildroot}%{_datadir}/polkit-1/
echo "[Theme]" > %{buildroot}%{_datadir}/kde-settings/kde-profile/default/share/config/plasmarc
echo "name=RHEL7" >> %{buildroot}%{_datadir}/kde-settings/kde-profile/default/share/config/plasmarc
echo "[KSplash]" > %{buildroot}%{_datadir}/kde-settings/kde-profile/default/share/config/ksplashrc
echo "Theme=RHEL7" >> %{buildroot}%{_datadir}/kde-settings/kde-profile/default/share/config/ksplashrc
perl -pi -e "s,^Theme=.*,Theme=/usr/share/kde4/apps/kdm/themes/RHEL7," %{buildroot}%{_sysconfdir}/kde/kdm/kdmrc
perl -pi -e "s,^HomeURL=.*,HomeURL=file:///usr/share/doc/HTML/index.html," %{buildroot}%{_datadir}/kde-settings/kde-profile/default/share/config/konquerorrc
perl -pi -e "s,^View0_URL=.*,View0_URL=file:///usr/share/doc/HTML/index.html," %{buildroot}%{_datadir}/kde-settings/kde-profile/default/share/apps/konqueror/profiles/webbrowsing
%endif


%files 
%doc COPYING
%config(noreplace) %{_sysconfdir}/profile.d/kde.*
%{_sysconfdir}/kde/env/env.sh
%{_sysconfdir}/kde/env/gtk2_rc_files.sh
%if 0%{?fedora}
%{_sysconfdir}/kde/env/fedora-bookmarks.sh
%{_datadir}/kde-settings/
%{_prefix}/lib/rpm/plasma4.prov
%{_prefix}/lib/rpm/plasma4.req
%{_prefix}/lib/rpm/fileattrs/plasma4.attr
%{_datadir}/polkit-1/rules.d/11-fedora-kde-policy.rules
%endif
%config(noreplace) /etc/pam.d/kcheckpass
%config(noreplace) /etc/pam.d/kscreensaver
# drop noreplace, so we can be sure to get the new kiosk bits
%config %{_sysconfdir}/kderc
%config %{_sysconfdir}/kde4rc
%dir %{_datadir}/kde-settings/
%dir %{_datadir}/kde-settings/kde-profile/
%{_datadir}/kde-settings/kde-profile/default/
%{_kde4_appsdir}/kconf_update/fedora-kde-display-handler.*
%if 0%{?rhel}
%exclude %{_datadir}/kde-settings/kde-profile/default/share/apps/plasma-desktop/init/00-defaultLayout.js
%endif

%files minimal
%{_datadir}/kde-settings/kde-profile/minimal/
%{_sysconfdir}/X11/xinit/xinitrc.d/20-kdedirs-minimal.sh

%post kdm
%{?systemd_post:%systemd_post kdm.service}
(grep '^UserAuthDir=/var/run/kdm$' %{_sysconfdir}/kde/kdm/kdmrc > /dev/null && \
 sed -i.rpmsave -e 's|^UserAuthDir=/var/run/kdm$|#UserAuthDir=/tmp|' \
 %{_sysconfdir}/kde/kdm/kdmrc
) ||:

%preun kdm
%{?systemd_preun:%systemd_preun kdm.service}

%postun kdm
%{?systemd_postun}

%files kdm
%doc COPYING
%config(noreplace) /etc/pam.d/kdm*
# compat symlink
%{_datadir}/config/kdm
%dir %{_sysconfdir}/kde/kdm
%config(noreplace) %{_sysconfdir}/kde/kdm/kdmrc
%dir %{_localstatedir}/lib/kdm
%config(noreplace) %{_localstatedir}/lib/kdm/backgroundrc
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sysconfdir}/kde/kdm/README*
%config(noreplace) %{_sysconfdir}/kde/kdm/Xaccess
%config(noreplace) %{_sysconfdir}/kde/kdm/Xresources
%config(noreplace) %{_sysconfdir}/kde/kdm/Xsession
%config(noreplace) %{_sysconfdir}/kde/kdm/Xsetup
%config(noreplace) %{_sysconfdir}/kde/kdm/Xwilling
# own logrotate.d/ avoiding hard dep on logrotate
%dir %{_sysconfdir}/logrotate.d
%config(noreplace) %{_sysconfdir}/logrotate.d/kdm
%{_tmpfilesdir}/kdm.conf
%attr(0711,root,root) %dir %{_localstatedir}/run/kdm
%attr(0711,root,root) %dir %{_localstatedir}/run/xdmctl
%{_unitdir}/kdm.service

%files ksplash
%{_datadir}/kde-settings/kde-profile/default/share/config/ksplashrc

%files plasma
%{_datadir}/kde-settings/kde-profile/default/share/config/plasmarc

%files pulseaudio
# nothing, this is a metapackage

%files -n qt-settings
%doc COPYING
%config(noreplace) %{_sysconfdir}/Trolltech.conf
%config(noreplace) %{_sysconfdir}/profile.d/qt-graphicssystem.*


%changelog
* Fri May 31 2013 Martin Briza <mbriza@redhat.com> - 19-23
- remove Console login menu option from KDM (#966095)

* Wed May 22 2013 Than Ngo <than@redhat.com> - 19-22
- disable java by default 

* Tue May 21 2013 Rex Dieter <rdieter@fedoraproject.org> 19-21
- cleanup systemd macros
- kde-settings-kdm is misusing preset files (#963898)
- prune %%changelog

* Mon May 13 2013 Rex Dieter <rdieter@fedoraproject.org> 19-20
- plymouth-quit-wait service fails resulting in very long boot time (#921785)

* Wed Apr 24 2013 Martin Briza <mbriza@redhat.com> 19-19
- Return to the usual X server invocation in case there's no systemd provided wrapper

* Wed Apr 24 2013 Daniel Vrátil <dvratil@redhat.com> 19-18
- remove Mugshot from Konqueror bookmarks (#951279)

* Mon Apr 15 2013 Martin Briza <mbriza@redhat.com> 19-17.2
- so depending on /lib/systemd/systemd-multi-seat-x is considered a broken dependency - kdm depends on systemd instead

* Sat Apr 13 2013 Rex Dieter <rdieter@fedoraproject.org> 19-17.1
- use %%_tmpfilesdir macro

* Thu Apr 11 2013 Martin Briza <mbriza@redhat.com> 19-17
- Use /lib/systemd/systemd-multi-seat-x as the X server in KDM

* Wed Apr 03 2013 Martin Briza <mbriza@redhat.com> 19-16
- Fedora release number was wrong in /etc/kde/kdm/kdmrc

* Wed Apr 03 2013 Martin Briza <mbriza@redhat.com> 19-15
- Fixed KDM theme name in /etc

* Thu Mar 28 2013 Martin Briza <mbriza@redhat.com> 19-14
- Changed the strings in the settings to Schrödinger's Cat instead of Spherical Cow

* Mon Feb 04 2013 Kevin Kofler <Kevin@tigcc.ticalc.org> 19-13.1
- Requires: polkit-js-engine

* Mon Jan 28 2013 Rex Dieter <rdieter@fedoraproject.org> 19-13
- +fedora-kde-display-handler kconf_update script

* Wed Dec 05 2012 Rex Dieter <rdieter@fedoraproject.org> 19-12
- plasma4.req: be more careful wrt IFS

* Tue Dec 04 2012 Rex Dieter <rdieter@fedoraproject.org> 19-11
- plasma4.req: allow for > 1 scriptengine

* Tue Nov 27 2012 Dan Vratil <dvratil@redhat.com> 19-10
- provide kwin rules to fix maximization of some Gtk2 apps

* Sun Nov 11 2012 Rex Dieter <rdieter@fedoraproject.org> 19-9.1
- fixup kdmrc for upgraders who had UserAuthDir=/var/run/kdm

* Thu Nov 08 2012 Rex Dieter <rdieter@fedoraproject.org> 19-9
- tighten permissions on /var/run/kdm
- support /var/run/xdmctl

* Fri Oct 12 2012 Kevin Kofler <Kevin@tigcc.ticalc.org> 19-8
- kslideshow.kssrc: use xdg-user-dir instead of hardcoding $HOME/Pictures

* Fri Oct 12 2012 Kevin Kofler <Kevin@tigcc.ticalc.org> 19-7
- port 11-fedora-kde-policy from old pkla format to new polkit-1 rules (#829881)
- nepomukstrigirc: index translated xdg-user-dirs (dvratil, #861129)

* Thu Sep 27 2012 Dan Vratil <dvratil@redhat.com> 19-5
- fix indexing paths in nepomukstrigirc (#861129)

* Mon Sep 24 2012 Rex Dieter <rdieter@fedoraproject.org> 19-4
- -minimal subpkg

* Tue Sep 04 2012 Dan Vratil <dvratil@redhat.com> 19-3
- add 81-fedora-kdm-preset (#850775)
- start kdm.service after livesys-late.service

* Wed Aug 29 2012 Rex Dieter <rdieter@fedoraproject.org> - 19-1
- reset Version to match target fedora release (19)
- kdm.pam: pam_gnome_keyring.so should be loaded after pam_systemd.so (#852723)

* Tue Aug 21 2012 Martin Briza <mbriza@redhat.com> 4.9-5
- Change strings to Fedora 18 (Spherical Cow)
- bump system_kde_theme_ver to 17.91

* Sat Aug 11 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9-2.1
- -kdm: drop old stuff, fix systemd scriptlets

* Thu Aug 09 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9-2
- /etc/pam.d/kdm missing: -session optional pam_ck_connector.so (#847114)

* Wed Aug 08 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.9-1
- adapt kdm for display manager rework feature (#846145)

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.8-16.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jun 29 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8-16
- qt-graphicssystem.csh: fix typo s|/usr/bin/lspci|/usr/sbin/lspci| (#827440)

* Wed Jun 13 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8-15.1
- kde-settings-kdm conflicts with gdm (#819254)

* Wed Jun 13 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8-15
- qt-settings does NOT fully quallify path to lspci in /etc/profile.d/qt-graphicssystem.{csh,sh} (#827440)

* Fri May 25 2012 Than Ngo <than@redhat.com> - 4.8-14.1
- rhel/fedora condtion

* Wed May 16 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8-14
- Pure Qt applications can't use KDE styles outside of KDE (#821062)

* Tue May 15 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8-13
- kdmrc: GUIStyle=Plastique (#810161)

* Mon May 14 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8-12
- drop hack/workaround for bug #750423
- move /etc/tmpfiles.d => /usr/lib/tmpfiles.d

* Thu May 10 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8-10
- +qt-settings: move cirrus workaround(s) here (#810161)

* Wed May 09 2012 Than Ngo <than@redhat.com> - 4.8-8.2
- fix rhel condition

* Tue May 08 2012 Than Ngo <than@redhat.com> - 4.8-8.1
- add workaround for cirrus

* Mon Apr 30 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8-8
- fix application/x-rpm mimetype defaults

* Wed Apr 18 2012 Than Ngo <than@redhat.com> - 4.8-7.1
- add rhel condition

* Mon Mar 19 2012 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.8-7
- plasma4.prov: change spaces in runner names to underscores

* Tue Feb 28 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8-6
- kslideshow.kssrc: include some sane/working defaults

* Tue Feb 14 2012 Jaroslav Reznik <jreznik@redhat.com> 4.8-5
- fix plasmarc Beefy Miracle reference

* Tue Feb 14 2012 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.8-4
- kdmrc: GreetString=Fedora 17 (Beefy Miracle)
- kdmrc, ksplashrc, plasmarc: s/Verne/BeefyMiracle/g (for the artwork themes)
- bump system_kde_theme_ver to 16.91

* Mon Jan 16 2012 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.8-3
- merge the plasma-rpm tarball into the SVN trunk and thus the main tarball

* Mon Jan 16 2012 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.8-2
- allow org.kde.kcontrol.kcmclock.save without password for wheel again
- Requires: polkit (instead of polkit-desktop-policy)

* Mon Jan 16 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8-1
- kwinrc: drop [Compositing] Enabled=false

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.7-14.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sat Nov 19 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7-14
- add explicit apper defaults
- add script to init $XDG_DATA_HOME (to workaround bug #750423)

* Mon Oct 31 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7-13.4
- make new-subpkgs Requires: %%name for added safety

* Mon Oct 31 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7-13.3
- -ksplash: Requires: system-ksplash-theme >= 15.90
- -plasma: Requires: system-plasma-desktoptheme >= 15.90

* Mon Oct 31 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7-13.2
- -kdm: Requires: system-kdm-theme >= 15.90

* Mon Oct 31 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7-13.1
- -kdm: Requires: verne-kdm-theme (#651305) 

* Fri Oct 21 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7-13
- s/kpackagekit/apper/ configs
- drop gpg-agent scripts (autostarts on demand now)

* Sat Oct 15 2011 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.7-12
- disable the default Plasma digital-clock's displayEvents option by default

* Wed Oct 12 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7-11
- krunnerrc: org.kde.events_runnerEnabled=false
- follow Packaging:Tmpfiles.d guildelines

* Wed Oct 05 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7-10
- don't spam syslog if pam-gnome-keyring is not present (#743044)

* Fri Sep 30 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7-9
- -kdm: add explicit Requires: xorg-x11-xinit

* Tue Sep 27 2011 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.7-8
- plasma4.prov: don't trust the Name of script engines, always use the API

* Thu Sep 22 2011 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.7-7
- ship the Plasma RPM dependency generators only on F17+
- use xz tarball
- don't rm Makefile, no longer in the tarball
- set up a folder view on the desktop by default for new users (#740676)
- kdmrc: set MinShowUID=-1 (use /etc/login.defs) instead of 500 (#717115)
- -kdm: Requires: kdm >= 4.7.1-2 (required for MinShowUID=-1)

* Wed Aug 31 2011 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.7-6
- put under the MIT license as agreed with the other contributors

* Sun Aug 21 2011 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.7-5
- fix the RPM dependency generators to also accept ServiceTypes= (#732271)

* Sun Aug 21 2011 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.7-4
- add the RPM dependency generators for Plasma (GSoC 2011), as Source1 for now

* Tue Aug 02 2011 Jaroslav Reznik <jreznik@redhat.com> 4.7-3
- update to Verne theming/branding

* Wed Jul 13 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7-2
- kmixrc: [Global] startkdeRestore=false

* Thu Mar 24 2011 Rex Dieter <rdieter@fedoraproject.org> 4.6-10
- konq webbrowsing profile: start.fedoraproject.org
- konq tabbedbrowsing : start.fedoraproject.org, fedoraproject.org/wiki/KDE

* Tue Mar 22 2011 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.6-9
- Requires: polkit-desktop-policy

* Thu Mar 10 2011 Rex Dieter <rdieter@fedoraproject.org> 4.6-8
- s/QtCurve/oxygen-gtk/

* Mon Mar 07 2011 Rex Dieter <rdieter@fedoraproject.org> 4.6-7
- use adwaita-cursor-theme

* Mon Mar 07 2011 Rex Dieter <rdieter@fedoraproject.org> 4.6-6
- use lovelock-kdm-theme
- /var/log/kdm.log is never clean up (logrotate) (#682761)
- -kdm, move xterm dep to comps (#491251)

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.6-4.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Feb 07 2011 Rex Dieter <rdieter@fedoraproject.org> 4.6-4
- de-Laughlin-ize theming, be genericish/upstream (for now)
- kcminputrc: theme=dmz-aa, Requires: dmz-cursor-themes (#675509)

* Tue Feb 01 2011 Rex Dieter <rdieter@fedoraproject.org> 4.6-3
- add support for the postlogin PAM stack to kdm (#665060)

* Wed Dec 08 2010 Rex Dieter <rdieter@fedoraproject.org> 4.6-2.1
- %post kdm : sed -e 's|-nr|-background none|' kdmrc (#659684)
- %post kdm : drop old stuff

* Fri Dec 03 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.6-2
- drop old Conflicts
- Xserver-1.10: Fatal server error: Unrecognized option: -nr (#659684)

* Mon Nov 29 2010 Rex Dieter <rdieter@fedoraproject.org> 4.6-1 
- init 4.6 
- /var/run/kdm/ fails to be created on boot (#657785)

* Thu Nov 11 2010 Rex Dieter <rdieter@fedoraproject.org> 4.5-11
- kdebugrc: DisableAll=true (#652367)

* Fri Oct 29 2010 Rex Dieter <rdieter@fedoraproject.org> 4.5-10
- kdmrc: UserList=false

* Thu Oct 14 2010 Rex Dieter <rdieter@fedoraproject.org> 4.5-9
- drop plasma-{desktop,netbook}-appletsrc
- plasmarc: set default plasma(-netbook) themes (#642763)

* Sat Oct 09 2010 Rex Dieter <rdieter@fedoraproject.org> 4.5-8
- rename 00-start-here script to ensure it runs (again).

* Fri Oct 08 2010 Rex Dieter <rdieter@fedoraproject.org> 4.5-7
- make 00-start-here-kde-fedora.js look for simplelauncher too (#615621)

* Tue Sep 28 2010 Rex Dieter <rdieter@fedoraproject.org> 4.5-6
- move plasma-desktop bits into kde-settings/kde-profile instead

* Tue Sep 28 2010 Rex Dieter <rdieter@fedoraproject.org> 4.5-5
- 00-start-here-kde-fedora.js plasma updates script (#615621)

* Fri Sep 03 2010 Rex Dieter <rdieter@fedoraproject.org> 4.5-4
- kdeglobals : drop [Icons] Theme=Fedora-KDE (#615621)

* Tue Aug 03 2010 Jaroslav Reznik <jreznik@redhat.com> 4.5-3
- laughlin kde theme as default

* Mon Apr 26 2010 Rex Dieter <rdieter@fedoraproject.org> 4.5-2
- kde-settings-kdm depends on xorg-x11-xdm (#537608)

* Tue Apr 13 2010 Rex Dieter <rdieter@fedoraproject.org> 4.5-1.1
- -kdm: own /var/spool/gdm (#551310,#577482)

* Tue Feb 23 2010 Rex Dieter <rdieter@fedoraproject.org> 4.5-1
- 4.5 branch for F-14
- (re)enable kdebug

* Tue Feb 23 2010 Rex Dieter <rdieter@fedoraproject.org> 4.4-13
- disable kdebug by default (#560508)

* Mon Feb 22 2010 Jaroslav Reznik <jreznik@redhat.com> 4.4-12
- added dist tag to release

* Mon Feb 22 2010 Jaroslav Reznik <jreznik@redhat.com> 4.4-11
- goddard kde theme as default

* Sat Jan 30 2010 Rex Dieter <rdieter@fedoraproject.org> 4.4-10
- move /etc/kde/kdm/backgroundrc => /var/lib/kdm/backgroundrc (#522513)
- own /var/lib/kdm (regression, #442081)

* Fri Jan 29 2010 Rex Dieter <rdieter@fedoraproject.org> 4.4-9
- krunnerrc: disable nepomuksearch plugin by default (#559977)

* Wed Jan 20 2010 Rex Dieter <rdieter@fedoraproject.org> 4.4-8
- plasma-netbook workspace has no wallpaper configured (#549996)

* Tue Jan 05 2010 Rex Dieter <rdieter@fedoraproject.org> 4.4-7
- externalize fedora-kde-icon-theme (#547701)

* Wed Dec 30 2009 Rex Dieter <rdieter@fedoraproject.org> 4.4-6.1
- -kdm: Requires: kdm

* Fri Dec 25 2009 Rex Dieter <rdieter@fedoraproject.org> 4.4-6
- use qtcurve-gtk2 by default (#547700)

* Wed Dec 23 2009 Rex Dieter <rdieter@fedoraproject.org> 4.4-4
- enable nepomuk, with some conservative defaults (#549436)

* Tue Dec 01 2009 Rex Dieter <rdieter@fedoraproject.org> 4.4-3
- kdmrc: ServerArgsLocal=-nr , for better transition from plymouth

* Tue Dec 01 2009 Rex Dieter <rdieter@fedoraproject.org> 4.4-2
- kdmrc: revert to ServerVTs=-1 (#475890)

* Sun Nov 29 2009 Rex Dieter <rdieter@fedoraproject.org> 4.4-1
- -pulseaudio: drop xine-lib-pulseaudio (subpkg no longer exists)
